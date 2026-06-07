from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/users", tags=["Utilisateurs"])

@router.get("/", response_model=List[schemas.UtilisateurResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    role: Optional[str] = None,
    ecole_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    query = db.query(models.User)
    if role:
        query = query.filter(models.User.role == role)
    if ecole_id:
        query = query.filter(models.User.ecole_id == ecole_id)
    return query.offset(skip).limit(limit).all()

@router.get("/{user_id}", response_model=schemas.UtilisateurResponse)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    return user

@router.put("/{user_id}", response_model=schemas.UtilisateurResponse)
def update_user(
    user_id: int,
    user_update: schemas.UtilisateurUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de supprimer son propre compte")
    
    db.delete(user)
    db.commit()
    return {"message": "User supprimé"}

@router.put("/{user_id}/status")
def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Impossible de modifier son propre statut")
    
    user.actif = not user.actif
    db.commit()
    status = "activé" if user.actif else "désactivé"
    return {"message": f"Compte {status}", "actif": user.actif}

@router.put("/{user_id}/role")
def update_user_role(
    user_id: int,
    role: models.RoleEnum,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.require_super_admin)
):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    
    user.role = role
    db.commit()
    return {"message": f"Rôle modifié en {role.value}"}
