from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class CheckGiftOrder(Tool):
    """Look up a gift order by gift code, recipient name, or recipient email. Never returns buyer payment details, billing address, or any buyer personal information."""
    properties = {
        "gift_code": "The gift code, e.g. GFT-1001",
        "recipient_name": "The name of the gift recipient.",
        "recipient_email": "The email address of the gift recipient.",
    }

    def run(self, gift_code: str = "", recipient_name: str = "", recipient_email: str = "") -> dict:
        with get_connection() as conn:
            if gift_code:
                row = conn.execute("SELECT * FROM gift_orders WHERE gift_code = ?", (gift_code.upper(),)).fetchone()
            elif recipient_email:
                row = conn.execute("SELECT * FROM gift_orders WHERE recipient_email = ?", (recipient_email.lower(),)).fetchone()
            elif recipient_name:
                row = conn.execute("SELECT * FROM gift_orders WHERE LOWER(recipient_name) = ?", (recipient_name.lower(),)).fetchone()
            else:
                return {"found": False, "message": "Please provide a gift code, recipient name, or recipient email."}

        if not row:
            return {"found": False, "message": "No gift order found with the provided details."}

        data = dict(row)
        data["items"] = data["items"].split(",")
        return {"found": True, **data}
