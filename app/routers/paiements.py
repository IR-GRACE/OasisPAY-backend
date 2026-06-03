from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Utilisateur, Etudiant, Paiement
from ..services.wonya_pay import WonyaPayService
from ..auth import get_current_user
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
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

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
        return {"status": "processing", "reference": result.get("RefTransa"), "message": "Paiement initié"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))