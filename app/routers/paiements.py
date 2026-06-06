from fastapi import APIRouter, Depends, HTTPException
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
        # Enregistrer le paiement avec le statut PENDING
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
        return {"status": "processing", "reference": result.get("reference"), "message": "Paiement initié, veuillez confirmer sur votre téléphone"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))