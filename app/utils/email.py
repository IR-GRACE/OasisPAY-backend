import os
import smtplib
from email.message import EmailMessage

def send_payment_receipt(to_email, etudiant_nom, montant, reference):
    # Pour test : affiche simplement dans les logs. En production, configurer un serveur SMTP.
    print(f"EMAIL envoyé à {to_email}: Paiement {montant} FC pour {etudiant_nom} - ref {reference}")
    # Exemple avec SendGrid (décommentez si vous avez la clé)
    # msg = EmailMessage()
    # msg.set_content(f"Cher parent,\n\nLe paiement de {montant} FC pour {etudiant_nom} a été effectué.\nRéférence: {reference}\n\nMerci.")
    # msg['Subject'] = "Confirmation de paiement OasisPAY"
    # msg['From'] = "no-reply@oasispay.com"
    # msg['To'] = to_email
    # with smtplib.SMTP('smtp.sendgrid.net', 587) as smtp:
    #     smtp.starttls()
    #     smtp.login('apikey', os.getenv('SENDGRID_API_KEY'))
    #     smtp.send_message(msg)