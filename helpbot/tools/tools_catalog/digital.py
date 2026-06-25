from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class GetDigitalPurchase(Tool):
    """Verify whether a customer owns a digital product and check the status of their download link."""
    properties = {
        "email": "The customer's email address.",
        "product_title": "The title of the digital product.",
    }

    def run(self, email: str, product_title: str, session_email: str | None = None) -> dict:
        if session_email and email.lower().strip() != session_email:
            return {"owned": False, "email": email, "product_title": product_title, "message": "Access denied — email does not match session identity."}
        with get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM digital_purchases WHERE email = ? AND product_title = ?",
                (email.lower().strip(), product_title.lower().strip())
            ).fetchone()
        if not row:
            return {"owned": False, "email": email, "product_title": product_title, "message": "No purchase found for this email and product."}
        return {"email": email, "product_title": product_title, **dict(row)}


class ResendDownloadLink(Tool):
    """Resend a fresh download link for a digital product to the customer's email. IMPORTANT: Only call this tool after get_digital_purchase has confirmed the customer owns the product. Never call this tool if ownership has not been verified in the current conversation."""
    properties = {
        "email": "The customer's email address.",
        "product_title": "The title of the digital product.",
    }

    def run(self, email: str, product_title: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute(
                "SELECT owned FROM digital_purchases WHERE email = ? AND product_title = ?",
                (email.lower().strip(), product_title.lower().strip()),
            ).fetchone()
        if not row or not row["owned"]:
            return {"success": False, "email": email, "product_title": product_title, "message": "Cannot resend — no verified purchase found for this email and product."}
        return {
            "success": True,
            "email": email,
            "product_title": product_title,
            "message": f"A fresh download link for '{product_title}' has been sent to {email}. It will be valid for 7 days with up to 3 downloads.",
        }
