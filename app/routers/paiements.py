from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Paiement

router = APIRouter(prefix="/paiements", tags=["paiements"])

@router.post("/webhook/shwary")
async def shwary_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    transaction_id = payload.get("id")
    status = payload.get("status")
    reference = payload.get("referenceId")
    amount = payload.get("amount")
    currency = payload.get("currency")
    failure_reason = payload.get("failureReason")
    # Chercher le paiement par référence
    paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
    if paiement:
        paiement.statut = status.upper()
        if status == "completed":
            paiement.date_paiement = datetime.utcnow()
        if status in ["failed", "cancelled"]:
            paiement.failure_reason = failure_reason
        db.commit()
    else:
        # Optionnel : créer un nouveau paiement si besoin
        pass
    return {"status": "ok"}