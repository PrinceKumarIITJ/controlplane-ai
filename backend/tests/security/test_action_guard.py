import pytest
import time
import uuid
import json
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal, init_db
from app.services.target_service import TargetService
from app.models.domain import AgentActionModel, DecisionModel, ApprovalTokenModel, HumanReviewModel
from app.core.crypto import generate_approval_token, compute_parameters_hash

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    init_db()
    TargetService.reset_counters()
    db = SessionLocal()
    try:
        db.query(ApprovalTokenModel).delete()
        db.query(HumanReviewModel).delete()
        db.query(DecisionModel).delete()
        db.query(AgentActionModel).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
    yield
    TargetService.reset_counters()

def test_sec_01_direct_agent_bypass():
    """SEC-01: Direct agent request without ControlPlane token must be denied (Target Calls = 0)."""
    response = client.post("/mock/payment", json={
        "action_id": "act_direct_bypass",
        "parameters": {"vendor": "Vendor X", "amount": 5000000}
    })
    assert response.status_code == 403
    assert response.json()["status"] == "DENIED"
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_02_missing_token_header():
    """SEC-02: Missing token header must be denied (Target Calls = 0)."""
    response = client.post("/mock/payment", json={
        "action_id": "act_missing_header",
        "parameters": {"vendor": "Vendor X", "amount": 5000000}
    })
    assert response.status_code == 403
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_03_forged_token_signature():
    """SEC-03: Forged HMAC token signature must be denied (Target Calls = 0)."""
    payload = {
        "token_id": "tok_forged",
        "action_id": "act_forged",
        "action_type": "PAYMENT",
        "target": "vendor_payment_service",
        "parameters_hash": compute_parameters_hash({"vendor": "Vendor X", "amount": 5000000}),
        "decision_id": "dec_forged",
        "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY",
        "policy_version": "1.0.0",
        "nonce": "n_forged_123",
        "issued_at": int(time.time()),
        "expires_at": int(time.time()) + 300
    }
    forged_token = generate_approval_token(payload, secret_key="ATTACKER_WRONG_SECRET")
    
    response = client.post(
        "/mock/payment",
        json={"action_id": "act_forged", "parameters": {"vendor": "Vendor X", "amount": 5000000}},
        headers={"X-ControlPlane-Approval-Token": forged_token}
    )
    assert response.status_code == 401
    assert "signature mismatch" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_04_expired_token():
    """SEC-04: Expired token must be denied (Target Calls = 0)."""
    db = SessionLocal()
    action_id = f"act_expired_{uuid.uuid4().hex[:6]}"
    decision_id = f"dec_expired_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_exp_{uuid.uuid4().hex[:6]}"
    nonce = f"n_exp_{uuid.uuid4().hex[:8]}"
    params = {"vendor": "Vendor X", "amount": 5000000}
    params_hash = compute_parameters_hash(params)
    
    act = AgentActionModel(
        action_id=action_id, action_type="PAYMENT", target="vendor_payment_service",
        parameters_hash=params_hash, parameters_json=json.dumps(params),
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=87.0, reversibility="IRREVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=decision_id, action_id=action_id, assurance_level="L3",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=87.0,
        detection_confidence=0.9, composite_risk=0.4, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)
    db.commit()

    payload = {
        "token_id": token_id, "action_id": action_id, "action_type": "PAYMENT",
        "target": "vendor_payment_service", "parameters_hash": params_hash,
        "decision_id": decision_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": nonce, "issued_at": int(time.time()) - 600, "expires_at": int(time.time()) - 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=action_id, decision_id=decision_id,
        parameters_hash=params_hash, signature=token_str, nonce=nonce,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    response = client.post(
        "/mock/payment",
        json={"action_id": action_id, "parameters": params},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert response.status_code == 401
    assert "expired" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_05_replayed_token():
    """SEC-05: Reused/consumed token must be denied (Target Calls = 0 on replay)."""
    db = SessionLocal()
    action_id = f"act_replay_{uuid.uuid4().hex[:6]}"
    decision_id = f"dec_replay_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_rep_{uuid.uuid4().hex[:6]}"
    nonce = f"n_rep_{uuid.uuid4().hex[:8]}"
    params = {"vendor": "Vendor X", "amount": 5000000}
    params_hash = compute_parameters_hash(params)

    act = AgentActionModel(
        action_id=action_id, action_type="PAYMENT", target="vendor_payment_service",
        parameters_hash=params_hash, parameters_json=json.dumps(params),
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=87.0, reversibility="IRREVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=decision_id, action_id=action_id, assurance_level="L3",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=87.0,
        detection_confidence=0.9, composite_risk=0.4, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)

    payload = {
        "token_id": token_id, "action_id": action_id, "action_type": "PAYMENT",
        "target": "vendor_payment_service", "parameters_hash": params_hash,
        "decision_id": decision_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": nonce, "issued_at": int(time.time()), "expires_at": int(time.time()) + 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=action_id, decision_id=decision_id,
        parameters_hash=params_hash, signature=token_str, nonce=nonce,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    res1 = client.post(
        "/mock/payment",
        json={"action_id": action_id, "parameters": params},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert res1.status_code == 200
    assert TargetService.get_payment_api_call_count() == 1

    res2 = client.post(
        "/mock/payment",
        json={"action_id": action_id, "parameters": params},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert res2.status_code == 401
    assert "replay" in res2.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 1

def test_sec_06_action_id_mismatch():
    """SEC-06: Token action_id mismatch must be denied (Target Calls = 0)."""
    db = SessionLocal()
    act_a_id = f"act_A_{uuid.uuid4().hex[:6]}"
    act_b_id = f"act_B_{uuid.uuid4().hex[:6]}"
    dec_a_id = f"dec_A_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_mis_{uuid.uuid4().hex[:6]}"

    act = AgentActionModel(
        action_id=act_a_id, action_type="PAYMENT", target="vendor_payment_service",
        parameters_hash=compute_parameters_hash({"vendor": "Vendor A"}), parameters_json="{}",
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=87.0, reversibility="IRREVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=dec_a_id, action_id=act_a_id, assurance_level="L3",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=87.0,
        detection_confidence=0.9, composite_risk=0.4, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)

    payload = {
        "token_id": token_id, "action_id": act_a_id, "action_type": "PAYMENT",
        "target": "vendor_payment_service", "parameters_hash": compute_parameters_hash({"vendor": "Vendor A"}),
        "decision_id": dec_a_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": f"n_mis_{uuid.uuid4().hex[:6]}", "issued_at": int(time.time()), "expires_at": int(time.time()) + 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=act_a_id, decision_id=dec_a_id,
        parameters_hash=payload["parameters_hash"], signature=token_str, nonce=payload["nonce"],
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    response = client.post(
        "/mock/payment",
        json={"action_id": act_b_id, "parameters": {"vendor": "Vendor A"}},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert response.status_code == 401
    assert "mismatch" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_07_target_mismatch():
    """SEC-07: Token target mismatch must be denied (Target Calls = 0)."""
    db = SessionLocal()
    act_id = f"act_tgt_{uuid.uuid4().hex[:6]}"
    dec_id = f"dec_tgt_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_tgt_{uuid.uuid4().hex[:6]}"

    act = AgentActionModel(
        action_id=act_id, action_type="PAYMENT", target="catalog_faq_service",
        parameters_hash=compute_parameters_hash({"item_id": "cat_1"}), parameters_json="{}",
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=10.0, reversibility="EASILY_REVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=dec_id, action_id=act_id, assurance_level="L0",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=10.0,
        detection_confidence=0.9, composite_risk=0.1, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)

    payload = {
        "token_id": token_id, "action_id": act_id, "action_type": "PAYMENT",
        "target": "catalog_faq_service", "parameters_hash": compute_parameters_hash({"item_id": "cat_1"}),
        "decision_id": dec_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": f"n_tgt_{uuid.uuid4().hex[:6]}", "issued_at": int(time.time()), "expires_at": int(time.time()) + 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=act_id, decision_id=dec_id,
        parameters_hash=payload["parameters_hash"], signature=token_str, nonce=payload["nonce"],
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    response = client.post(
        "/mock/payment",
        json={"action_id": act_id, "parameters": {"item_id": "cat_1"}},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert response.status_code == 401
    assert "target mismatch" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_08_parameter_tampering():
    """SEC-08: Parameter tampering attack must be denied (Target Calls = 0)."""
    db = SessionLocal()
    action_id = f"act_tamper_{uuid.uuid4().hex[:6]}"
    decision_id = f"dec_tamper_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_tamper_{uuid.uuid4().hex[:6]}"
    original_params = {"vendor": "Vendor Legitimate", "amount": 5000}
    tampered_params = {"vendor": "Vendor Attacker", "amount": 5000000}
    params_hash = compute_parameters_hash(original_params)

    act = AgentActionModel(
        action_id=action_id, action_type="PAYMENT", target="vendor_payment_service",
        parameters_hash=params_hash, parameters_json=json.dumps(original_params),
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=10.0, reversibility="IRREVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=decision_id, action_id=action_id, assurance_level="L1",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=10.0,
        detection_confidence=0.9, composite_risk=0.1, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)

    payload = {
        "token_id": token_id, "action_id": action_id, "action_type": "PAYMENT",
        "target": "vendor_payment_service", "parameters_hash": params_hash,
        "decision_id": decision_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": f"n_tamper_{uuid.uuid4().hex[:6]}", "issued_at": int(time.time()), "expires_at": int(time.time()) + 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=action_id, decision_id=decision_id,
        parameters_hash=params_hash, signature=token_str, nonce=payload["nonce"],
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    response = client.post(
        "/mock/payment",
        json={"action_id": action_id, "parameters": tampered_params},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert response.status_code == 401
    assert "parameter tampering" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_09_policy_version_mismatch():
    """SEC-09: Policy version mismatch must be denied (Target Calls = 0)."""
    db = SessionLocal()
    action_id = f"act_pol_ver_{uuid.uuid4().hex[:6]}"
    decision_id = f"dec_pol_ver_{uuid.uuid4().hex[:6]}"
    token_id = f"tok_ver_{uuid.uuid4().hex[:6]}"
    params = {"vendor": "Vendor X", "amount": 5000}
    params_hash = compute_parameters_hash(params)

    act = AgentActionModel(
        action_id=action_id, action_type="PAYMENT", target="vendor_payment_service",
        parameters_hash=params_hash, parameters_json=json.dumps(params),
        agent_id="agent_1", user_id="usr_1", application_id="finance_app_prod",
        business_impact=10.0, reversibility="IRREVERSIBLE", status="AUTHORIZED"
    )
    dec = DecisionModel(
        decision_id=decision_id, action_id=action_id, assurance_level="L1",
        performance_risk=0.1, cost_risk=0.1, responsibility_risk=0.0, business_impact=10.0,
        detection_confidence=0.9, composite_risk=0.1, decision="ALLOW", warning=False,
        policy_id="FINANCE_AGENT_POLICY", policy_version="2.0.0", reason="Allowed", rule_triggered="DEFAULT"
    )
    db.add(act)
    db.add(dec)

    payload = {
        "token_id": token_id, "action_id": action_id, "action_type": "PAYMENT",
        "target": "vendor_payment_service", "parameters_hash": params_hash,
        "decision_id": decision_id, "application_id": "finance_app_prod",
        "policy_id": "FINANCE_AGENT_POLICY", "policy_version": "1.0.0",
        "nonce": f"n_ver_{uuid.uuid4().hex[:6]}", "issued_at": int(time.time()), "expires_at": int(time.time()) + 300
    }
    token_str = generate_approval_token(payload)

    token_model = ApprovalTokenModel(
        token_id=token_id, action_id=action_id, decision_id=decision_id,
        parameters_hash=params_hash, signature=token_str, nonce=payload["nonce"],
        policy_id="FINANCE_AGENT_POLICY", policy_version="1.0.0",
        issued_at=payload["issued_at"], expires_at=payload["expires_at"], status="ISSUED"
    )
    db.add(token_model)
    db.commit()
    db.close()

    response = client.post(
        "/mock/payment",
        json={"action_id": action_id, "parameters": params},
        headers={"X-ControlPlane-Approval-Token": token_str}
    )
    assert response.status_code == 401
    assert "policy version" in response.json()["message"].lower()
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_10_human_rejection():
    """SEC-10: Execution attempt after human rejection must be denied (Target Calls = 0)."""
    action_id = f"act_reject_{uuid.uuid4().hex[:6]}"
    action_payload = {
        "action_id": action_id,
        "action_type": "PAYMENT",
        "target": "vendor_payment_service",
        "parameters": {"vendor": "Vendor X", "amount": 5000000, "currency": "INR"},
        "requester": {"agent_id": "finance_agent_v2", "user_id": "usr_emp_4412", "application_id": "finance_app_prod"},
        "reversibility": "IRREVERSIBLE"
    }
    gov_res = client.post("/api/v1/govern/action", json=action_payload)
    assert gov_res.status_code == 200
    assert gov_res.json()["decision"] == "HUMAN_REVIEW"
    assert gov_res.json()["approval_token"] is None

    rev_res = client.post(f"/api/v1/review/{action_id}", json={
        "reviewer_id": "usr_compliance_lead",
        "review_action": "REJECT",
        "reason": "Unapproved vendor transaction request."
    })
    assert rev_res.status_code == 200
    assert rev_res.json()["approval_token"] is None

    target_res = client.post("/mock/payment", json={
        "action_id": action_id,
        "parameters": {"vendor": "Vendor X", "amount": 5000000, "currency": "INR"}
    })
    assert target_res.status_code == 403
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_11_unauthorized_reviewer():
    """SEC-11: Invalid review request on non-existent action must fail (Target Calls = 0)."""
    rev_res = client.post("/api/v1/review/act_non_existent", json={
        "reviewer_id": "usr_unauthorized",
        "review_action": "APPROVE"
    })
    assert rev_res.status_code == 400
    assert TargetService.get_payment_api_call_count() == 0

def test_sec_12_valid_approved_execution():
    """SEC-12: Valid human-approved action generates HMAC token and succeeds (Target Calls = 1)."""
    action_id = f"act_approve_{uuid.uuid4().hex[:6]}"
    action_payload = {
        "action_id": action_id,
        "action_type": "PAYMENT",
        "target": "vendor_payment_service",
        "parameters": {"vendor": "Vendor X", "amount": 5000000, "currency": "INR"},
        "requester": {"agent_id": "finance_agent_v2", "user_id": "usr_emp_4412", "application_id": "finance_app_prod"},
        "reversibility": "IRREVERSIBLE"
    }
    gov_res = client.post("/api/v1/govern/action", json=action_payload)
    assert gov_res.status_code == 200
    assert gov_res.json()["decision"] == "HUMAN_REVIEW"

    rev_res = client.post(f"/api/v1/review/{action_id}", json={
        "reviewer_id": "usr_compliance_lead",
        "review_action": "APPROVE",
        "reason": "Verified vendor invoice INV-2026-99."
    })
    assert rev_res.status_code == 200
    approval_token = rev_res.json()["approval_token"]
    assert approval_token is not None

    target_res = client.post(
        "/mock/payment",
        json={
            "action_id": action_id,
            "parameters": {"vendor": "Vendor X", "amount": 5000000, "currency": "INR"}
        },
        headers={"X-ControlPlane-Approval-Token": approval_token}
    )
    assert target_res.status_code == 200
    assert target_res.json()["status"] == "SUCCESS"
    assert TargetService.get_payment_api_call_count() == 1
