from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Utilisateur
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def get_users(db: Session = Depends(get_db), current_user: Utilisateur = Depends(get_current_user)):
    users = db.query(Utilisateur).all()
    return [{"id": u.id, "email": u.email, "nom": u.nom, "prenom": u.prenom, "role": u.role, "actif": u.actif} for u in users]