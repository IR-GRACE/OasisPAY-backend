from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import User, Etudiant, Classe, Paiement, AuditLog
from .auth import get_current_user, require_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# =========================
# DASHBOARD
# =========================

@router.get("/dashboard")
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    total_users = db.query(User).count()
    total_etudiants = db.query(Etudiant).count()
    total_classes = db.query(Classe).count()
    total_paiements = db.query(Paiement).count()

    total_encaisse = (
        db.query(func.sum(Paiement.montant))
        .scalar()
        or 0
    )

    return {
        "total_users": total_users,
        "total_etudiants": total_etudiants,
        "total_classes": total_classes,
        "total_paiements": total_paiements,
        "total_encaisse": float(total_encaisse)
    }

# =========================
# USERS
# =========================

@router.get("/users")
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    users = db.query(User).all()

    return [
        {
            "id": u.id,
            "email": u.email,
            "nom": u.nom,
            "prenom": u.prenom,
            "role": u.role,
            "actif": u.actif
        }
        for u in users
    ]

@router.put("/users/{user_id}/disable")
def disable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    user.actif = False
    db.commit()

    return {"message": "Utilisateur désactivé"}

@router.put("/users/{user_id}/enable")
def enable_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    user.actif = True
    db.commit()

    return {"message": "Utilisateur activé"}

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(404, "Utilisateur introuvable")

    db.delete(user)
    db.commit()

    return {"message": "Utilisateur supprimé"}

# =========================
# AUDIT LOGS
# =========================

@router.get("/audit-logs")
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(100)
        .all()
    )

    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "action": l.action,
            "status": l.status,
            "created_at": str(l.created_at)
        }
        for l in logs
    ]
