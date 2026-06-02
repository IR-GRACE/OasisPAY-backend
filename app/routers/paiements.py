from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.orm import Session
from datetime import datetime
from ..database import get_db
from ..models import Paiement, Utilisateur, Etudiant
from ..schemas import PaiementCreate, PaiementResponse
from ..services.wonya_pay import WonyaPayService
from .auth import get_current_user
import uuid

router = APIRouter(prefix="/paiements", tags=["Paiements"])

@router.post("/", response_model=PaiementResponse)
async def initier_paiement(
    paiement: PaiementCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Récupérer l'étudiant
    etudiant = db.query(Etudiant).filter(Etudiant.id == paiement.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    if etudiant.parent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    # Générer une référence unique
    reference = f"OASIS-{uuid.uuid4().hex[:8].upper()}"

    # Créer le paiement en base
    nouveau_paiement = Paiement(
        reference=reference,
        etudiant_id=paiement.etudiant_id,
        montant=paiement.montant,
        type_frais=paiement.type_frais,
        methode_paiement=paiement.methode_paiement,
        numero_telephone=paiement.numero_telephone,
        statut="en_attente"
    )
    db.add(nouveau_paiement)
    db.commit()
    db.refresh(nouveau_paiement)

    # Appel à WonyaPay
    try:
        wonya = WonyaPayService()
        operateur = paiement.methode_paiement.upper()
        result = await wonya.initier_paiement(
            montant=paiement.montant,
            telephone=paiement.numero_telephone,
            operateur=operateur,
            reference=reference,
            description=f"Frais {paiement.type_frais} - {etudiant.nom} {etudiant.prenom}"
        )
        nouveau_paiement.transaction_id = result.get("transaction_id")
        nouveau_paiement.statut = "initie"
        db.commit()
        return nouveau_paiement
    except Exception as e:
        nouveau_paiement.statut = "echoue"
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook/wonya")
async def wonya_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook WonyaPay"""
    data = await request.json()
    reference = data.get("reference")
    statut = data.get("status")
    transaction_id = data.get("transaction_id")
    paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
    if paiement:
        if statut == "SUCCESS":
            paiement.statut = "paye"
            paiement.date_paiement = datetime.utcnow()
        else:
            paiement.statut = "echoue"
        paiement.transaction_id = transaction_id
        db.commit()
    return {"status": "ok"}

@router.get("/{reference}", response_model=PaiementResponse)
def get_paiement(reference: str, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    return paiement

