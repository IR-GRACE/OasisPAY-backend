from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Admin, Utilisateur
from .auth import get_current_user, get_password_hash
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/admin", tags=["Administration"])

async def require_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "admin", "directeur"]:
        raise HTTPException(status_code=403, detail="Accès non autorisé")
    return current_user

@router.post("/create-super-admin")
def create_super_admin(db: Session = Depends(get_db)):
    # Chercher dans admins maintenant
    admin = db.query(Admin).filter(Admin.email == "stypojulvier009@gmail.com").first()
    if not admin:
        new_admin = Admin(
            nom="JULVIER",
            prenom="MUKENDI",
            email="stypojulvier009@gmail.com",
            telephone="0994477720",
            hashed_password=get_password_hash("2003"),
            role="super_admin",
            actif=True
        )
        db.add(new_admin)
        db.commit()
        return {"message": "Super admin créé"}
    return {"message": "Admin existe déjà"}

@router.get("/users")
def get_all_users(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    # Retourner les admins ET les utilisateurs normaux
    admins = db.query(Admin).all()
    utilisateurs = db.query(Utilisateur).all()
    return {"admins": admins, "utilisateurs": utilisateurs}

@router.put("/users/{user_id}/status")
def toggle_user_status(user_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    # Chercher d'abord dans admins
    user = db.query(Admin).filter(Admin.id == user_id).first()
    if not user:
        user = db.query(Utilisateur).filter(Utilisateur.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.actif = not user.actif
    db.commit()
    return {"message": f"Compte {'activé' if user.actif else 'désactivé'}"}


@router.post("/assign-parent/{etudiant_id}/{parent_id}")
async def assign_parent(
    etudiant_id: int,
    parent_id: int,
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(require_admin)
):
    etudiant = db.query(Etudiant).filter(Etudiant.id == etudiant_id).first()
    if not etudiant:
        raise HTTPException(status_code=404, detail="Étudiant non trouvé")
    parent = db.query(Utilisateur).filter(Utilisateur.id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent non trouvé")
    etudiant.parent_id = parent_id
    db.commit()
    return {"message": "Parent associé avec succès"}