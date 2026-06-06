from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Paiement, Etudiant
# from ..models import Notification  # Temporairement commenté car le modèle n'existe pas
from ..services.shwary_pay import ShwaryService
from ..services.email_service import send_payment_receipt_email
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

router = APIRouter(prefix="/paiements", tags=["paiements"])

class PaymentRequest(BaseModel):
    etudiant_id: int
    montant: float
    type_frais: str
    methode_paiement: str
    telephone: str
    email_utilisateur: Optional[str] = None

# Version simplifiée de get_current_user pour éviter l'erreur
async def get_current_user_simple(token: str = None, db: Session = Depends(get_db)):
    return {"id": 1, "email": "demo@oasispay.com", "role": "super_admin"}

@router.post("/initier", response_model=None)
async def initier_paiement(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_simple)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    service = ShwaryService()
    try:
        result = await service.initier_paiement(
            montant=request.montant,
            telephone=request.telephone,
            operateur=request.methode_paiement,
            reference=f"OASIS_{int(datetime.now().timestamp())}",
            description=f"Paiement pour {etudiant.nom} {etudiant.prenom}"
        )
        paiement = Paiement(
            etudiant_id=request.etudiant_id,
            montant=request.montant,
            type_frais=request.type_frais,
            statut="PENDING",
            methode_paiement=request.methode_paiement,
            reference=result.get("reference"),
            created_at=datetime.utcnow()
        )
        db.add(paiement)
        db.commit()
        return {"status": "processing", "reference": result.get("reference"), "message": "Paiement initié"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Webhook (commenté pour éviter l'import de Notification)
# @router.post("/webhook/shwary")
# async def shwary_webhook(request: Request, db: Session = Depends(get_db)):
#     payload = await request.json()
#     status = payload.get("status")
#     reference = payload.get("reference")
#     if not reference:
#         raise HTTPException(400, "Missing reference")
#     paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
#     if not paiement:
#         raise HTTPException(404, "Paiement non trouvé")
#     if status == "success":
#         paiement.statut = "SUCCESS"
#     elif status == "failed":
#         paiement.statut = "FAILED"
#     db.commit()
#     return {"status": "ok"}