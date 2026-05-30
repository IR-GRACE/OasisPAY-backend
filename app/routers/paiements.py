from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..models import Paiement
from .auth import get_current_user
import uuid
from datetime import datetime

router = APIRouter(prefix="/paiements", tags=["Paiements"])

@router.get("/")
def get_paiements(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Paiement).order_by(Paiement.date.desc()).all()

@router.post("/")
def create_paiement(paiement_data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    reference = f"PAY-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"
    new_paiement = Paiement(**paiement_data, reference=reference, caissier_id=current_user.id)
    db.add(new_paiement)
    db.commit()
    db.refresh(new_paiement)
    return new_paiement

@router.get("/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    total_etudiants = db.query(Paiement).count()
    total_encaisse = db.query(func.sum(Paiement.montant)).filter(Paiement.statut == "paye").scalar() or 0
    return {
        "total_etudiants": total_etudiants,
        "total_encaisse": float(total_encaisse),
        "taux_paiement": 0,
        "paiements_en_attente": 0
    }
