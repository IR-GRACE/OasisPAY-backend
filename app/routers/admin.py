from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import Utilisateur
from .auth import get_current_user, get_password_hash

router = APIRouter(prefix="/admin", tags=["Administration"])

async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "admin_ecole"]:
        raise HTTPException(status_code=403, detail="Droits administrateur requis")
    return current_user

@router.post("/create-super-admin")
def create_super_admin(db: Session = Depends(get_db)):
    email = "stypojulvier009@mail.com"
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        admin = Utilisateur(
            nom="Administrateur",
            prenom="Principal",
            email=email,
            hashed_password=get_password_hash("Mukend123"),
            role="super_admin",
            actif=True,
            is_verified=True
        )
        db.add(admin)
        db.commit()
        return {"message": "Super admin créé"}
    return {"message": "Admin existe déjà"}

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    return db.query(Utilisateur).all()

@router.put("/users/{user_id}/status")
def toggle_user_status(user_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.actif = not user.actif
    db.commit()
    return {"message": f"Compte {'activé' if user.actif else 'désactivé'}"}
