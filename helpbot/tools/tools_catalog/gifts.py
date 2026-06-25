from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckGiftOrder(Tool):
    """Look up a gift order by gift code, recipient name, or recipient email. Never returns buyer payment details, billing address, or any buyer personal information."""
    properties = {
        "gift_code": "The gift code, e.g. GFT-1001",
        "recipient_name": "The name of the gift recipient.",
        "recipient_email": "The email address of the gift recipient.",
    }

    def run(self, gift_code: str = "", recipient_name: str = "", recipient_email: str = "", session_email: str | None = None) -> dict:
        with get_connection() as conn:
            if gift_code:
                row = conn.execute("SELECT * FROM gift_orders WHERE gift_code = ?", (gift_code.upper(),)).fetchone()
            elif recipient_email:
                row = conn.execute("SELECT * FROM gift_orders WHERE recipient_email = ?", (recipient_email.lower(),)).fetchone()
            elif recipient_name:
                row = conn.execute("SELECT * FROM gift_orders WHERE LOWER(recipient_name) LIKE ?", (f"%{recipient_name.lower()}%",)).fetchone()
            else:
                return {"found": False, "message": "Please provide a gift code, recipient name, or recipient email."}

        if not row:
            return {"found": False, "message": "No gift order found with the provided details."}

        return {
            "found": True,
            "gift_code": row["gift_code"],
            "status": row["status"],
            "recipient_name": row["recipient_name"],
            "recipient_email": row["recipient_email"],
            "items": row["items"].split(","),
            "delivered_on": row["delivered_on"],
            "estimated_delivery": row["estimated_delivery"],
            "estimated_dispatch": row["estimated_dispatch"],
        }
