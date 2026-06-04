from celery import Celery
import smtplib
from email.message import EmailMessage
import os

celery_app = Celery('oasispay', broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))

@celery_app.task
def send_payment_receipt_email(to_email, etudiant_nom, montant, reference):
    msg = EmailMessage()
    msg.set_content(f"Cher parent,\n\nLe paiement de {montant} FC pour {etudiant_nom} a été effectué.\nRéférence: {reference}\n\nMerci d'utiliser OasisPAY.")
    msg['Subject'] = "Confirmation de paiement OasisPAY"
    msg['From'] = "no-reply@oasispay.com"
    msg['To'] = to_email
    # Configurez votre serveur SMTP dans les variables d'environnement
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.sendgrid.net')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)
    else:
        print(f"Email non envoyé (config manquante): {to_email}")