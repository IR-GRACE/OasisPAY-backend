import os
import httpx
from typing import Optional

async def send_email(to: str, subject: str, body: str, html: Optional[str] = None):
    api_key = os.getenv("BREVO_API_KEY")
    if not api_key:
        print("BREVO_API_KEY non définie, email non envoyé")
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={"api-key": api_key, "Content-Type": "application/json"},
            json={
                "sender": {"email": "noreply@oasispay.com", "name": "OasisPAY"},
                "to": [{"email": to}],
                "subject": subject,
                "htmlContent": html or f"<p>{body}</p>"
            }
        )