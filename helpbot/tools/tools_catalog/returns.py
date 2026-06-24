from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckReturnEligibility(Tool):
    """Check whether a customer's order is eligible for a return."""
    properties = {
        "order_id": "The order ID to check return eligibility for, e.g. PT-1001",
    }

    def run(self, order_id: str) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM return_eligibility WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row:
            return {"found": False, "order_id": order_id}
        return {"found": True, **dict(row)}


class GetRefundStatus(Tool):
    """Get the current processing stage of a refund for a given order."""
    properties = {
        "order_id": "The order ID to look up refund status for, e.g. PT-1001",
    }

    def run(self, order_id: str) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM refunds WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row:
            return {"found": False, "order_id": order_id, "message": "No refund found for this order."}
        return {"found": True, **dict(row)}
