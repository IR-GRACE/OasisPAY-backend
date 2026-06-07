from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from datetime import timedelta
import secrets

router = APIRouter(prefix="/auth", tags=["Authentification"])

@router.post("/login", response_model=schemas.TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Compte non vérifié")
    
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role.value})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.post("/register", response_model=schemas.UtilisateurResponse)
def register(
    user_data: schemas.UtilisateurCreate,
    db: Session = Depends(get_db)
):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    hashed = auth.get_password_hash(user_data.password)
    new_user = models.User(
        nom=user_data.nom,
        prenom=user_data.prenom,
        email=user_data.email,
        telephone=user_data.telephone,
        hashed_password=hashed,
        role=user_data.role,
        ecole_id=user_data.ecole_id,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.get("/me", response_model=schemas.UtilisateurResponse)
def get_current_user(
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return current_user

@router.put("/me", response_model=schemas.UtilisateurResponse)
def update_current_user(
    user_update: schemas.UtilisateurUpdate,
    current_user: models.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/refresh")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    payload = auth.decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token invalide")
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not user.actif:
        raise HTTPException(status_code=401, detail="User non trouvé")
    
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role.value})
    return {"access_token": access_token, "token_type": "bearer"}
