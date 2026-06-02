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
    paiement: PaiementCreate,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == paiement.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    if etudiant.parent_id != current_user.id:
        raise HTTPException(status_code=403, detail="Non autorisé")

    reference = f"OASIS-{uuid.uuid4().hex[:8].upper()}"
    nouveau_paiement = Paiement(
        reference=reference,
        etudiant_id=paiement.etudiant_id,
        montant=paiement.montant,
        devise = paiement.devise if hasattr(paiement, "devise") else "CDF"`n            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ) else 'CDF',
        type_frais=paiement.type_frais,
        methode_paiement=paiement.methode_paiement,
        numero_telephone=paiement.numero_telephone,
        statut="en_attente"
    )            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    db.add(nouveau_paiement)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    db.commit()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    db.refresh(nouveau_paiement)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )

    try:
        wonya = WonyaPayService()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        operateur = paiement.methode_paiement.upper()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        result = await wonya.initier_paiement(
            montant=paiement.montant,
            telephone=paiement.numero_telephone,
            operateur=operateur,
            reference=reference,
            description=f"Frais {paiement.type_frais} - {etudiant.nom} {etudiant.prenom}"
        )            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        nouveau_paiement.transaction_id = result.get("transaction_id")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        nouveau_paiement.statut = "initie"
        db.commit()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        return nouveau_paiement
    except Exception as e:
        nouveau_paiement.statut = "echoue"
        db.commit()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        raise HTTPException(status_code=400, detail=str(e)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ))            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )

@router.post("/webhook/wonya")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
async def wonya_webhook(request: Request, db: Session = Depends(get_db)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ))            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ):
    try:
        data = await request.json()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    except:
        return {"status": "error", "message": "Invalid JSON"}
    
    reference = data.get("reference")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    statut = data.get("status")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    transaction_id = data.get("transaction_id")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    
    if reference:
        paiement = db.query(Paiement)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ).filter(Paiement.reference == reference)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ).first()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
        if paiement:
            if statut == "SUCCESS":
                paiement.statut = "paye"
                paiement.date_paiement = datetime.utcnow()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
            else:
                paiement.statut = "echoue"
            if transaction_id:
                paiement.transaction_id = transaction_id
            db.commit()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
            return {"status": "ok", "message": "Paiement mis à jour"}
    return {"status": "ignored", "message": "Référence non trouvée"}

@router.get("/{reference}", response_model=PaiementResponse)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
def get_paiement(reference: str, db: Session = Depends(get_db)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ), current_user: Utilisateur = Depends(get_current_user)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ))            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ):
    paiement = db.query(Paiement)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ).filter(Paiement.reference == reference)            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            ).first()            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")            nouveau_paiement = Paiement(
                reference=reference,
                etudiant_id=paiement.etudiant_id,
                montant=paiement.montant,
                devise=paiement.devise if hasattr(paiement, 'devise') else 'CDF',
                type_frais=paiement.type_frais,
                methode_paiement=paiement.methode_paiement,
                numero_telephone=paiement.numero_telephone,
                statut="en_attente"
            )
    return paiement


