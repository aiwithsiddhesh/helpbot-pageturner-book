from helpbot.tools.engine.base import Tool
from helpbot.db import get_connection


class GetAccountStatus(Tool):
    """Look up a customer account status by email address to assist with login or access issues."""
    properties = {
        "email": "The customer's email address.",
    }

    def run(self, email: str, session_email: str | None = None) -> dict:
        if session_email and email.lower().strip() != session_email:
            return {"found": False, "email": email, "message": "Access denied — email does not match session identity."}
        with get_connection() as conn:
            row = conn.execute("SELECT * FROM accounts WHERE email = ?", (email.lower().strip(),)).fetchone()
        if not row:
            return {"found": False, "email": email, "message": "No account found with this email address."}
        return {"found": True, **dict(row)}
