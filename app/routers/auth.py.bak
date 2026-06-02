from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import Utilisateur
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

SECRET_KEY = os.getenv("SECRET_KEY", "secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

router = APIRouter(prefix="/auth", tags=["Authentification"])

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user or not user.actif:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    
    access_token = create_access_token(data={"sub": user.email})
    role_value = user.role.value if hasattr(user.role, 'value') else user.role
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "nom": user.nom,
            "prenom": getattr(user, 'prenom', ''),
            "email": user.email,
            "role": role_value,
            "actif": user.actif
        }
    }

@router.get("/me")
def get_current_user_info(current_user = Depends(get_current_user)):
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else current_user.role
    return {
        "id": current_user.id,
        "nom": current_user.nom,
        "prenom": getattr(current_user, 'prenom', ''),
        "email": current_user.email,
        "role": role_value,
        "actif": current_user.actif
    }

class RegisterRequest(BaseModel):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str
    role: str = "parent"

@router.post("/register")
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    hashed = get_password_hash(user_data.password)
    new_user = Utilisateur(
        email=user_data.email,
        hashed_password=hashed,
        nom=user_data.nom,
        prenom=user_data.prenom,
        telephone=user_data.telephone,
        role=user_data.role,
        actif=True,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Compte créé avec succès", "user_id": new_user.id}


class RegisterRequest(BaseModel):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str
    role: str = "parent"

@router.post("/register")
def register(user_data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Utilisateur).filter(Utilisateur.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")
    hashed = get_password_hash(user_data.password)
    new_user = Utilisateur(
        email=user_data.email,
        hashed_password=hashed,
        nom=user_data.nom,
        prenom=user_data.prenom,
        telephone=user_data.telephone,
        role=user_data.role,
        actif=True,
        is_verified=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Compte créé avec succès", "user_id": new_user.id}

