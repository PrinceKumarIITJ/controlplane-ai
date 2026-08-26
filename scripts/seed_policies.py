import json
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.database import SessionLocal, init_db
from app.models.domain import PolicyModel

def seed_policies():
    init_db()
    db = SessionLocal()
    policies_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "policies"))
    
    for filename in os.listdir(policies_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(policies_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            existing = db.query(PolicyModel).filter(
                PolicyModel.policy_id == data["policy_id"],
                PolicyModel.version == data["version"]
            ).first()
            
            if not existing:
                policy = PolicyModel(
                    policy_id=data["policy_id"],
                    version=data["version"],
                    name=data["name"],
                    application_id=data["application_id"],
                    rules_json=json.dumps(data),
                    is_active=True
                )
                db.add(policy)
                print(f"Seeded policy: {data['policy_id']} v{data['version']}")
            else:
                print(f"Policy already exists: {data['policy_id']} v{data['version']}")
                
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_policies()
