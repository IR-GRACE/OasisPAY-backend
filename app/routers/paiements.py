from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Utilisateur, Etudiant, Paiement
from ..services.wonya_pay import WonyaPayService
from ..auth import get_current_user
from typing import Optional
from datetime import datetime
# from reportlab.pdfgen import canvas
# from io import BytesIO
# from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/paiements", tags=["paiements"])

class PaymentRequest(BaseModel):
    etudiant_id: int
    montant: float
    type_frais: str
    methode_paiement: str
    telephone: str
    email_utilisateur: Optional[str] = None

@router.post("/initier")
async def initier_paiement(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Ã‰tudiant non trouvÃ©")

    service = WonyaPayService()
    try:
        result = await service.initier_paiement(
            montant=request.montant,
            telephone=request.telephone,
            operateur=request.methode_paiement,
            description=f"Paiement pour {etudiant.nom} {etudiant.prenom}"
        )
        paiement = Paiement(
            etudiant_id=request.etudiant_id,
            montant=request.montant,
            type_frais=request.type_frais,
            statut="PENDING",
            methode_paiement=request.methode_paiement,
            reference=result.get("RefTransa"),
            created_at=datetime.utcnow()
        )
        db.add(paiement)
        db.commit()
        return {"status": "processing", "reference": result.get("RefTransa"), "message": "Paiement initiÃ©"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Endpoint PDF temporairement dÃ©sactivÃ©\n# @router.get("/recu/{paiement_id}")
def generate_recu(
    paiement_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    paiement = db.query(Paiement).filter(Paiement.id == paiement_id).first()
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvÃ©")
    etudiant = db.query(Etudiant).filter(Etudiant.id == paiement.etudiant_id).first()
    buffer = BytesIO()
    c = canvas.Canvas(buffer)
    c.drawString(100, 800, f"ReÃ§u de paiement OasisPAY")
    c.drawString(100, 780, f"Ã‰tudiant: {etudiant.nom} {etudiant.prenom}")
    c.drawString(100, 760, f"Montant: {paiement.montant} FC")
    c.drawString(100, 740, f"Date: {paiement.created_at}")
    c.drawString(100, 720, f"RÃ©fÃ©rence: {paiement.reference}")
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=recu_{paiement_id}.pdf"})
@router.post("/webhook/shwary")
async def shwary_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    print(f"Webhook Shwary: {payload}")
    reference = payload.get("reference")
    status = payload.get("status")  # "success", "failed", "pending"
    if reference:
        paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
        if paiement:
            if status == "success":
                paiement.statut = "SUCCESS"
            elif status == "failed":
                paiement.statut = "FAILED"
            else:
                paiement.statut = "PROCESSING"
            db.commit()
    return {"status": "ok"}