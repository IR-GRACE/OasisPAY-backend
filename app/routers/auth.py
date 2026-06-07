from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict
import os
import secrets
from ..database import get_db
from ..models import User
from ..services.email_service import send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "prod_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email incorrect")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    access_token = create_access_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "nom": user.nom,
            "prenom": user.prenom,
            "role": user.role
        }
    }

@router.post("/register")
def register(user_data: dict, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_data["email"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    hashed = get_password_hash(user_data["password"])
    new_user = User(
        email=user_data["email"],
        nom=user_data.get("nom", ""),
        prenom=user_data.get("prenom", ""),
        telephone=user_data.get("telephone", ""),
        hashed_password=hashed,
        role="user",
        actif=True,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Compte créé avec succès", "user_id": new_user.id}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "telephone": current_user.telephone,
        "role": current_user.role
    }

@router.put("/me")
def update_profile(
    nom: Optional[str] = None,
    prenom: Optional[str] = None,
    telephone: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if nom is not None:
        current_user.nom = nom
    if prenom is not None:
        current_user.prenom = prenom
    if telephone is not None:
        current_user.telephone = telephone
    db.commit()
    db.refresh(current_user)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "telephone": current_user.telephone,
        "role": current_user.role
    }

# Stockage temporaire des tokens de réinitialisation (à remplacer par Redis)
reset_tokens: Dict[str, str] = {}

@router.post("/forgot-password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Ici vous pouvez appeler un service d'envoi d'email
    print(f"Lien de réinitialisation : https://oasispay-frontend.com/reset-password?token={token}")
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

@router.post("/change-password")
def change_password(old_password: str, new_password: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if not verify_password(old_password, current_user.hashed_password):
        raise HTTPException(status_code=401, detail="Ancien mot de passe incorrect")
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    return {"message": "Mot de passe modifié avec succès"}