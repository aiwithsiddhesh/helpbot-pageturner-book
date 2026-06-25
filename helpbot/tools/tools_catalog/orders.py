import random
import string

from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckOrderStatus(Tool):
    """Look up the current status of a customer order by order ID."""
    properties = {
        "order_id": "The order ID, e.g. PT-1001",
    }

    def run(self, order_id: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row or (session_email and row["email"] != session_email):
            return {"found": False, "access_denied": True, "message": "No order found or access denied."}
        return {"found": True, **dict(row)}


class CancelOrder(Tool):
    """Cancel a customer order by order ID. IMPORTANT: Only call this tool after the customer has explicitly confirmed they want to cancel. If the customer has not yet confirmed, ask them to confirm before calling this tool."""
    properties = {
        "order_id": "The order ID to cancel, e.g. PT-1001",
    }

    def run(self, order_id: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id.upper(),)).fetchone()
            if not row or (session_email and row["email"] != session_email):
                return {"success": False, "access_denied": True, "message": "No order found or access denied."}
            if row["status"] != "processing":
                return {
                    "success": False,
                    "reason": f"Order cannot be cancelled — it is already {row['status']}.",
                    "order_id": order_id,
                    "status": row["status"],
                }
            conn.execute("UPDATE orders SET status = 'cancelled' WHERE order_id = ?", (order_id.upper(),))
        return {"success": True, "order_id": order_id, "message": "Order successfully cancelled. A refund will be processed within 3–5 business days."}


class ReportOrderIssue(Tool):
    """Report a wrong item or missing item issue for a customer order. Use this for order content problems — wrong book received or items missing from the order."""
    properties = {
        "order_id": "The order ID with the issue, e.g. PT-1001",
        "issue_type": {"description": "The type of issue.", "enum": ["wrong_item", "missing_item"]},
        "details": "Brief description of the issue, e.g. which item was wrong or missing",
    }

    def run(self, order_id: str, issue_type: str, details: str = "", session_email: str | None = None) -> dict:
        case_id = "CASE-" + "".join(random.choices(string.digits, k=6))
        return {
            "case_id": case_id,
            "order_id": order_id,
            "issue_type": issue_type,
            "details": details,
            "message": f"Your issue has been logged under case {case_id}. Our team will review and contact you within 24 hours to resolve this.",
        }
