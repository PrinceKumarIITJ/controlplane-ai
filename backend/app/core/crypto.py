import hmac
import hashlib
import json
import base64
from typing import Dict, Any, Tuple, Optional
from app.config import settings

def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def base64url_decode(encoded_str: str) -> bytes:
    padding = "=" * (4 - (len(encoded_str) % 4))
    return base64.urlsafe_b64decode(encoded_str + padding)

def compute_parameters_hash(parameters: Dict[str, Any]) -> str:
    """Computes SHA-256 hex digest of sorted parameter dictionary."""
    canonical_json = json.dumps(parameters, sort_keys=True)
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

def generate_approval_token(payload: Dict[str, Any], secret_key: str = settings.CONTROLPLANE_TOKEN_SECRET) -> str:
    """
    Generates ControlPlane Approval Token string:
    base64url(canonical_payload_json).base64url(hmac_sha256_signature_hex)
    """
    canonical_payload_str = json.dumps(payload, sort_keys=True)
    payload_b64 = base64url_encode(canonical_payload_str.encode("utf-8"))

    signature_hex = hmac.new(
        secret_key.encode("utf-8"),
        canonical_payload_str.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    sig_b64 = base64url_encode(signature_hex.encode("utf-8"))
    return f"{payload_b64}.{sig_b64}"

def verify_approval_token_signature(token_str: str, secret_key: str = settings.CONTROLPLANE_TOKEN_SECRET) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Verifies base64url token structure and HMAC signature.
    Returns: (is_valid, decoded_payload_dict, error_message)
    """
    try:
        parts = token_str.split(".")
        if len(parts) != 2:
            return False, None, "Invalid token format structure (must be payload.signature)"

        payload_b64, sig_b64 = parts[0], parts[1]
        payload_json_str = base64url_decode(payload_b64).decode("utf-8")
        provided_sig_hex = base64url_decode(sig_b64).decode("utf-8")

        payload_dict = json.loads(payload_json_str)

        # Re-compute signature from canonical payload
        canonical_payload_str = json.dumps(payload_dict, sort_keys=True)
        expected_sig_hex = hmac.new(
            secret_key.encode("utf-8"),
            canonical_payload_str.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_sig_hex, provided_sig_hex):
            return False, None, "HMAC signature mismatch (tampered token signature)"

        return True, payload_dict, ""
    except Exception as e:
        return False, None, f"Token decoding failure: {str(e)}"
