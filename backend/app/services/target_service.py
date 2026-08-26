from typing import Dict, Any

class TargetService:
    _payment_api_call_count: int = 0
    _catalog_api_call_count: int = 0
    _transactions: list = []

    @classmethod
    def reset_counters(cls):
        cls._payment_api_call_count = 0
        cls._catalog_api_call_count = 0
        cls._transactions = []

    @classmethod
    def get_payment_api_call_count(cls) -> int:
        return cls._payment_api_call_count

    @classmethod
    def get_catalog_api_call_count(cls) -> int:
        return cls._catalog_api_call_count

    @classmethod
    def execute_mock_payment(cls, parameters: Dict[str, Any]) -> Dict[str, Any]:
        cls._payment_api_call_count += 1
        tx = {
            "transaction_id": f"tx_pay_{cls._payment_api_call_count:04d}",
            "vendor": parameters.get("vendor", "Vendor X"),
            "amount": parameters.get("amount", 0.0),
            "currency": parameters.get("currency", "INR"),
            "status": "SETTLED"
        }
        cls._transactions.append(tx)
        return {
            "status": "SUCCESS",
            "message": "Payment executed successfully by target system.",
            "transaction": tx,
            "target_api_calls": cls._payment_api_call_count
        }

    @classmethod
    def execute_mock_catalog(cls, parameters: Dict[str, Any]) -> Dict[str, Any]:
        cls._catalog_api_call_count += 1
        return {
            "status": "SUCCESS",
            "message": "Catalog FAQ details fetched successfully.",
            "catalog_item": {
                "item_id": parameters.get("item_id", "cat_faq_01"),
                "title": "Standard Vendor Onboarding FAQ",
                "policy_code": "FIN-POL-2026"
            },
            "target_api_calls": cls._catalog_api_call_count
        }
