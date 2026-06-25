from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class ValidatePromoCode(Tool):
    """Validate a promotional discount code to check if it is active and applicable."""
    properties = {
        "code": "The promotional code to validate, e.g. SUMMER20",
    }

    def run(self, code: str, session_email: str | None = None) -> dict:
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM promo_codes WHERE code = ?", (code.upper().strip(),)).fetchone()
        if not row:
            return {"found": False, "code": code, "message": "This promo code does not exist."}
        return {"found": True, **dict(row), "valid": bool(row["valid"])}


class GetLoyaltyStatus(Tool):
    """Get a customer's loyalty points balance and tier status by email address."""
    properties = {
        "email": "The customer's email address.",
    }

    def run(self, email: str, session_email: str | None = None) -> dict:
        if session_email and email.lower().strip() != session_email:
            return {"found": False, "email": email, "message": "Access denied — email does not match session identity."}
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM loyalty WHERE email = ?", (email.lower().strip(),)).fetchone()
        if not row:
            return {"found": False, "email": email, "message": "No loyalty account found with this email address."}
        return {"found": True, **dict(row)}
