from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Paiement, Utilisateur, Etudiant
from ..schemas import PaiementCreate, PaiementResponse
from ..services.wonya_pay import WonyaPayService
from .auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/paiements", tags=["Paiements"])

@router.post("/", response_model=PaiementResponse)
async def initier_paiement(
        print("DEBUG: paiement fields:", paiement.dict().keys())\n    paiement: PaiementCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Vérifier l'étudiant
    etudiant = db.query(Etudiant).filter(Etudiant.id == paiement.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    if etudiant.parent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    # Générer une référence unique
    reference = f"OASIS-{uuid.uuid4().hex[:8].upper()}"

    # Déterminer la devise
    devise = paiement.devise if hasattr(paiement, 'devise') and paiement.devise else "CDF"

    # Créer l'enregistrement en base
    nouveau_paiement = Paiement(
        reference=reference,
        etudiant_id=paiement.etudiant_id,
        montant=paiement.montant,
        devise=devise,
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
    try:
        data = await request.json()
    except:
        return {"status": "error", "message": "Invalid JSON"}

    reference = data.get("reference")
    statut = data.get("status")
    transaction_id = data.get("transaction_id")

    if reference:
        paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
        if paiement:
            if statut == "SUCCESS":
                paiement.statut = "paye"
                paiement.date_paiement = datetime.utcnow()
            else:
                paiement.statut = "echoue"
            if transaction_id:
                paiement.transaction_id = transaction_id
            db.commit()
            return {"status": "ok", "message": "Paiement mis à jour"}
    return {"status": "ignored", "message": "Référence non trouvée"}

@router.get("/{reference}", response_model=PaiementResponse)
def get_paiement(reference: str, db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    paiement = db.query(Paiement).filter(Paiement.reference == reference).first()
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    return paiement

