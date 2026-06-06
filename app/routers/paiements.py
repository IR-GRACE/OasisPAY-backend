from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Paiement, Etudiant
from ..services.shwary_pay import ShwaryService
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

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
    db: Session = Depends(get_db)
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
@router.post("/webhook/shwary")
async def shwary_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    print(f"=== SHWARY WEBHOOK RECEIVED ===")
    print(f"Payload: {payload}")
    transaction_id = payload.get("id")
    status = payload.get("status")
    reference = payload.get("referenceId")
    failure_reason = payload.get("failureReason")
    if not reference:
        return {"status": "ignored"}
    paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
    if not paiement:
        return {"status": "not found"}
    if status == "completed":
        paiement.statut = "SUCCESS"
        if transaction_id:
            paiement.transaction_id = transaction_id
    elif status in ("failed", "cancelled"):
        paiement.statut = "FAILED"
        paiement.failure_reason = failure_reason
    else:
        paiement.statut = "PROCESSING"
    db.commit()
    print(f"✅ Paiement {reference} mis à jour : {paiement.statut}")
    return {"status": "ok"}