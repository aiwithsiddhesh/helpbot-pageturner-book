from helpbot.tools.engine.base import Tool


class SetCustomerIdentity(Tool):
    """Record the email address the customer has provided so it can be used to look up their data. This does NOT grant access to protected tools — the customer must have completed email verification at session start for that. Call this when the customer mentions their email so you can address them correctly and pass it to lookup tools."""
    properties = {
        "email": "The customer's email address.",
    }

    def run(self, email: str, session_email: str | None = None) -> dict:
        # verified=False — only the OTP flow in main.py may grant a verified session.
        # _email is picked up by run_tool() to update the session without a global setter.
        return {
            "success": True,
            "_email": email,
            "message": f"Email recorded as {email}. Note: to access protected account data, identity must be verified via the email OTP sent at session start.",
        }
