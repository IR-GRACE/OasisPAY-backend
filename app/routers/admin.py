from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Utilisateur
from .auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    # Seul un super_admin peut lister tous les utilisateurs
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    users = db.query(Utilisateur).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "telephone": u.telephone,
            "role": u.role,
            "actif": u.actif,
            "is_verified": u.is_verified
        }
        for u in users
    ]

@router.put("/users/{user_id}/status")
def toggle_user_status(
    user_id: int,
    actif: bool,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Permission refusée")
    user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.actif = actif
    db.commit()
    return {"message": "Statut mis à jour"}