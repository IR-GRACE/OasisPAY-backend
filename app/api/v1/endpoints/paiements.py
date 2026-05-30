from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import uuid
from datetime import datetime
from ....database import get_db
from .... import models, schemas, auth
from ....services.wonyapay import wonyapay_service

router = APIRouter(prefix="/paiements", tags=["Paiements"])

class InitierPaiementRequest(BaseModel):
    etudiant_id: int
    montant: float
    type_frais: str
    telephone: str
    operateur: str  # ORANGE, AIRTEL, VODACOM

class VerifierPaiementRequest(BaseModel):
    transaction_id: str

@router.post("/initier-wonyapay")
async def initier_paiement_wonyapay(
    request: InitierPaiementRequest,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    """Initier un paiement via WonyaPay"""
    etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == request.etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    
    reference = f"OASISPAY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"
    
    # Créer le paiement en base avec statut EN_ATTENTE
    nouveau_paiement = models.Paiement(
        etudiant_id=request.etudiant_id,
        ecole_id=etudiant.ecole_id,
        montant=request.montant,
        type_frais=request.type_frais,
        statut=models.StatutPaiementEnum.EN_ATTENTE,
        methode_paiement=f"wonyapay_{request.operateur}",
        reference=reference,
        caissier_id=current_user.id
    )
    db.add(nouveau_paiement)
    db.commit()
    db.refresh(nouveau_paiement)
    
    try:
        result = await wonyapay_service.initier_paiement(
            montant=request.montant,
            telephone=request.telephone,
            operateur=request.operateur,
            reference=reference,
            description=f"Paiement {request.type_frais} - {etudiant.nom} {etudiant.prenom}"
        )
        
        nouveau_paiement.numero_transaction = result.get("transaction_id")
        db.commit()
        
        return {
            "success": True,
            "payment_id": nouveau_paiement.id,
            "reference": reference,
            "transaction_id": result.get("transaction_id"),
            "payment_url": result.get("payment_url"),
            "message": "Redirigez l'utilisateur vers l'URL de paiement"
        }
    except Exception as e:
        nouveau_paiement.statut = models.StatutPaiementEnum.ANNULE
        db.commit()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verifier-wonyapay")
async def verifier_paiement_wonyapay(
    request: VerifierPaiementRequest,
    db: Session = Depends(get_db)
):
    """Vérifier le statut d'un paiement WonyaPay"""
    try:
        result = await wonyapay_service.verifier_statut(request.transaction_id)
        
        paiement = db.query(models.Paiement).filter(
            models.Paiement.numero_transaction == request.transaction_id
        ).first()
        
        if paiement:
            if result.get("status") == "SUCCESS":
                paiement.statut = models.StatutPaiementEnum.PAYE
            elif result.get("status") == "FAILED":
                paiement.statut = models.StatutPaiementEnum.ANNULE
            db.commit()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook/wonyapay")
async def webhook_wonyapay(
    payload: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Webhook pour les notifications WonyaPay"""
    transaction_id = payload.get("transaction_id")
    status = payload.get("status")
    reference = payload.get("reference")
    
    paiement = db.query(models.Paiement).filter(
        models.Paiement.reference == reference
    ).first()
    
    if paiement:
        if status == "SUCCESS":
            paiement.statut = models.StatutPaiementEnum.PAYE
        elif status == "FAILED":
            paiement.statut = models.StatutPaiementEnum.ANNULE
        
        paiement.numero_transaction = transaction_id
        db.commit()
    
    return {"received": True}

@router.get("/historique")
def get_historique_paiements(
    etudiant_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    """Récupérer l'historique des paiements"""
    query = db.query(models.Paiement)
    
    if current_user.role == models.RoleEnum.PARENT:
        parent = db.query(models.Parent).filter(models.Parent.email == current_user.email).first()
        if parent:
            etudiant_ids = [e.id for e in parent.enfants]
            query = query.filter(models.Paiement.etudiant_id.in_(etudiant_ids))
    
    if etudiant_id:
        query = query.filter(models.Paiement.etudiant_id == etudiant_id)
    
    return query.order_by(models.Paiement.date.desc()).all()

@router.get("/recu/{paiement_id}")
def get_recu_paiement(
    paiement_id: int,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_active_user)
):
    """Générer et récupérer le reçu d'un paiement"""
    paiement = db.query(models.Paiement).filter(models.Paiement.id == paiement_id).first()
    if not paiement:
        raise HTTPException(status_code=404, detail="Paiement non trouvé")
    
    # Vérifier les droits d'accès
    if current_user.role == models.RoleEnum.PARENT:
        parent = db.query(models.Parent).filter(models.Parent.email == current_user.email).first()
        etudiant = db.query(models.Etudiant).filter(models.Etudiant.id == paiement.etudiant_id).first()
        if not parent or etudiant not in parent.enfants:
            raise HTTPException(status_code=403, detail="Accès non autorisé")
    
    # Génération du reçu (PDF)
    recu_url = f"/recus/{paiement.reference}.pdf"
    paiement.recu_url = recu_url
    db.commit()
    
    return {
        "recu_url": recu_url,
        "reference": paiement.reference,
        "montant": paiement.montant,
        "date": paiement.date,
        "etudiant_nom": paiement.etudiant.nom,
        "etudiant_prenom": paiement.etudiant.prenom
    }
