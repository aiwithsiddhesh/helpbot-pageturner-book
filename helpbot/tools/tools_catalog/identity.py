from helpbot.tools.engine.base import Tool
from helpbot.tools.engine.loader import set_session_email


class SetCustomerIdentity(Tool):
    """Set the customer's verified email as their session identity. Call this tool when the customer provides their email address for identity verification before accessing account or order data."""
    properties = {
        "email": "The customer's email address to set as session identity.",
    }

    def run(self, email: str, session_email: str | None = None) -> dict:
        set_session_email(email)
        return {"success": True, "message": f"Identity set for {email}. You can now access your account and order details."}
