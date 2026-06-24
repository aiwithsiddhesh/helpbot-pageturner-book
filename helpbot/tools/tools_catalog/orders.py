from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckOrderStatus(Tool):
    """Look up the current status of a customer order by order ID."""
    properties = {
        "order_id": "The order ID, e.g. PT-1001",
    }

    def run(self, order_id: str) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row:
            return {"found": False, "order_id": order_id}
        return {"found": True, **dict(row)}


class CancelOrder(Tool):
    """Cancel a customer order by order ID. IMPORTANT: Only call this tool after the customer has explicitly confirmed they want to cancel. If the customer has not yet confirmed, ask them to confirm before calling this tool."""
    properties = {
        "order_id": "The order ID to cancel, e.g. PT-1001",
    }

    def run(self, order_id: str) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM orders WHERE order_id = ?", (order_id.upper(),)).fetchone()
        if not row:
            return {"success": False, "reason": "Order not found.", "order_id": order_id}
        if row["status"] != "processing":
            return {
                "success": False,
                "reason": f"Order cannot be cancelled — it is already {row['status']}.",
                "order_id": order_id,
                "status": row["status"],
            }
        return {"success": True, "order_id": order_id, "message": "Order successfully cancelled. A refund will be processed within 3–5 business days."}
