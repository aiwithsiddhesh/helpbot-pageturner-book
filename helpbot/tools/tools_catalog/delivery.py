import random
import string

from helpbot.tools.engine.base import Tool


class ReportDeliveryIssue(Tool):
    """Report a delivery problem such as a missing parcel, damaged item, or wrong delivery. Only call this tool for shipping and delivery complaints. Do NOT call this for general complaints about product quality, pricing, or service."""
    properties = {
        "order_id": "The order ID related to the delivery issue",
        "issue_type": {"description": "The type of delivery issue.", "enum": ["not_received", "damaged", "wrong_address", "partial_delivery"]},
    }

    def run(self, order_id: str, issue_type: str, session_email: str | None = None) -> dict:
        case_id = "CASE-" + "".join(random.choices(string.digits, k=6))
        return {
            "case_id": case_id,
            "order_id": order_id,
            "issue_type": issue_type,
            "message": f"Your delivery issue has been logged under case {case_id}. Our team will investigate within 24 hours and contact you by email.",
        }
