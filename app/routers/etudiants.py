from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Etudiant
from .auth import get_current_user

router = APIRouter(prefix="/etudiants", tags=["Étudiants"])

@router.get("/")
def get_etudiants(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    return db.query(Etudiant).all()

@router.post("/")
def create_etudiant(etudiant_data: dict, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    new_etudiant = Etudiant(**etudiant_data)
    db.add(new_etudiant)
    db.commit()
    db.refresh(new_etudiant)
    return new_etudiant
