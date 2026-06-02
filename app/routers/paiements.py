from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from ..models import Utilisateur, Etudiant, Paiement
from ..services.flutterwave_pay import FlutterwaveService
from ..auth import get_current_user
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/paiements", tags=["paiements"])

class PaymentRequest(BaseModel):
    etudiant_id: int
    montant: float
    type_frais: str
    methode_paiement: str   # ORANGE, AIRTEL, VODACOM
    telephone: str
    email_utilisateur: Optional[str] = None

@router.post("/initier")
async def initier_paiement(
    request: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Vérifier l'étudiant
    etudiant = db.query(Etudiant).filter(Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")

    # Utiliser l'email du user courant si non fourni
    email = request.email_utilisateur or current_user.email

    service = FlutterwaveService()
    try:
        result = await service.initier_paiement(
            montant=request.montant,
            telephone=request.telephone,
            operateur=request.methode_paiement,
            email=email
        )
        # Enregistrement en base (statut PENDING)
        paiement = Paiement(
            etudiant_id=request.etudiant_id,
            montant=request.montant,
            type_frais=request.type_frais,
            statut="PENDING",
            methode_paiement=request.methode_paiement,
            reference=result.get("tx_ref"),
            created_at=datetime.utcnow()
        )
        db.add(paiement)
        db.commit()
        return {"status": "processing", "reference": result.get("tx_ref"), "message": "Paiement initié"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))