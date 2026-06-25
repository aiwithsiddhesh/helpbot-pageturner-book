from __future__ import annotations

import secrets
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def send_otp(email: str, otp: str, brevo_api_key: str, sender_email: str) -> bool:
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = brevo_api_key
    api = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=[{"email": email}],
        sender={"email": sender_email, "name": "PageTurner HelpBot"},
        subject="Your PageTurner verification code",
        text_content=f"Your verification code is: {otp}\n\nThis code expires in 5 minutes.",
    )
    try:
        api.send_transac_email(send_smtp_email)
        return True
    except ApiException:
        return False
