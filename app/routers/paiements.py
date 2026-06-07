from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Paiement

router = APIRouter(prefix="/paiements", tags=["paiements"])

@router.post("/webhook/shwary")
async def shwary_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
        reference = payload.get("referenceId")
        status = payload.get("status")
        if reference and status:
            paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
            if paiement:
                paiement.statut = status.upper()
                if status == "completed":
                    paiement.date_paiement = datetime.utcnow()
                db.commit()
        return {"status": "ok"}
    except Exception as e:
        # Log l'erreur mais retourne 200 pour éviter que Shwary réessaie
        print(f"Webhook error: {e}")
        return {"status": "error", "detail": str(e)}