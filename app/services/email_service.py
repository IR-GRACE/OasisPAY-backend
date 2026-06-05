import os
import smtplib
from email.message import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_verification_email(to_email: str, token: str):
    base_url = os.getenv("FRONTEND_URL", "https://oasispay-frontend.com")
    link = f"{base_url}/verify-email?token={token}"
    subject = "Vérifiez votre email – OasisPAY"
    body = f"Bonjour,\n\nMerci de vous être inscrit. Cliquez sur le lien :\n{link}\n\nL'équipe OasisPAY"
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv("SMTP_FROM_EMAIL")
    msg['To'] = to_email

    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")

    if not smtp_user or not smtp_pass:
        logger.warning("SMTP credentials not set")
        return

    with smtplib.SMTP(smtp_server, smtp_port) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_pass)
        smtp.send_message(msg)