from ..models import User
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..database import get_db
from ..models import Etudiant, User, Classe
from ..auth import get_current_user, require_admin
from typing import Optional

router = APIRouter(prefix="/etudiants", tags=["etudiants"])

@router.get("/")
def get_etudiants(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    classe_id: Optional[int] = Query(None),
    parent_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    query = db.query(Etudiant)
    if parent_id:
        query = query.filter(Etudiant.parent_id == parent_id)
    if classe_id:
        query = query.filter(Etudiant.classe_id == classe_id)
    if search:
        query = query.filter(
            or_(
                Etudiant.nom.ilike(f"%{search}%"),
                Etudiant.prenom.ilike(f"%{search}%"),
                Etudiant.matricule.ilike(f"%{search}%")
            )
        )
    total = query.count()
    etudiants = query.offset(skip).limit(limit).all()
    return {
        "total": total,
        "items": [{"id": e.id, "nom": e.nom, "prenom": e.prenom, "matricule": e.matricule, "classe_id": e.classe_id} for e in etudiants]
    }