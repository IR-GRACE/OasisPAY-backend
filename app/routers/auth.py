from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..database import get_db
from ..models import Utilisateur
import os

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "votre_cle_tres_secrete")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur non trouvé")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email incorrect")
    # Vérification du mot de passe désactivée pour la démo
    # if not verify_password(form_data.password, user.hashed_password):
    #     raise HTTPException(status_code=401, detail="Mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer", "user": {"id": user.id, "email": user.email, "nom": user.nom, "prenom": user.prenom, "role": user.role}}@router.post("/register")
def register(user_data: dict, db: Session = Depends(get_db)):
    existing = db.query(Utilisateur).filter(Utilisateur.email == user_data["email"]).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    hashed = get_password_hash(user_data["password"])
    new_user = Utilisateur(
        email=user_data["email"],
        nom=user_data["nom"],
        prenom=user_data["prenom"],
        telephone=user_data.get("telephone"),
        hashed_password=hashed,
        role=user_data.get("role", "user"),
        actif=True,
        is_verified=False
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # Ici vous pouvez envoyer un email de vérification
    return {"message": "Utilisateur créé. Vérifiez votre email."}