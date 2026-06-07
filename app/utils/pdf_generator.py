from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from io import BytesIO
import os

def generate_payment_receipt(etudiant_nom, etudiant_prenom, montant, date, reference, logo_path=None):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    if logo_path and os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            c.drawImage(img, width - 100, height - 80, width=80, height=80, preserveAspectRatio=True)
        except:
            pass
    c.drawString(50, height - 50, "OasisPAY - Reçu de paiement")
    c.drawString(50, height - 80, f"Étudiant: {etudiant_prenom} {etudiant_nom}")
    c.drawString(50, height - 110, f"Montant: {montant} FC")
    c.drawString(50, height - 140, f"Date: {date}")
    c.drawString(50, height - 170, f"Référence: {reference}")
    c.save()
    buffer.seek(0)
    return buffer