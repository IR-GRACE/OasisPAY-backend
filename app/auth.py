from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .database import get_db
from . import models, schemas
import os
import secrets

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Utilisateur:
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    payload = decode_token(token)
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(models.Utilisateur).filter(models.Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    
    return user

async def get_current_active_user(
    current_user: models.Utilisateur = Depends(get_current_user)
) -> models.Utilisateur:
    if not current_user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    return current_user

async def require_admin(
    current_user: models.Utilisateur = Depends(get_current_active_user)
) -> models.Utilisateur:
    if current_user.role not in [models.RoleEnum.SUPER_ADMIN, models.RoleEnum.ADMIN_ECOLE, models.RoleEnum.DIRECTEUR]:
        raise HTTPException(status_code=403, detail="Droits administrateur requis")
    return current_user

async def require_super_admin(
    current_user: models.Utilisateur = Depends(get_current_active_user)
) -> models.Utilisateur:
    if current_user.role != models.RoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=403, detail="Droits super administrateur requis")
    return current_user
