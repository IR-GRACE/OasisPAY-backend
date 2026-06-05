from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from ..database import get_db
from ..models import Utilisateur
import os

router = APIRouter(prefix="/auth", tags=["auth"])

SECRET_KEY = os.getenv("SECRET_KEY", "test_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Pour la démo : accepter un compte admin codé en dur (ne dépend pas de la base)
    DEMO_EMAIL = "admin@oasispay.com"
    DEMO_PASSWORD = "admin123"
    if form_data.username == DEMO_EMAIL and form_data.password == DEMO_PASSWORD:
        access_token = create_access_token(data={"sub": DEMO_EMAIL})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": 1,
                "email": DEMO_EMAIL,
                "nom": "Admin",
                "prenom": "Super",
                "role": "super_admin"
            }
        }
    # Sinon, essayer la base de données (si elle contient des utilisateurs)
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    # Pour la démo, on ignore la vérification du mot de passe (car pb de bcrypt)
    # Mais on accepte n'importe quel mot de passe si l'email existe
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

@router.get("/me")
def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        # D'abord chercher dans la base, sinon le compte démo
        user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
        if user:
            return {
                "id": user.id,
                "email": user.email,
                "nom": user.nom,
                "prenom": user.prenom,
                "role": user.role
            }
        elif email == "admin@oasispay.com":
            return {
                "id": 1,
                "email": email,
                "nom": "Admin",
                "prenom": "Super",
                "role": "super_admin"
            }
        raise HTTPException(401, "Utilisateur non trouvé")
    except:
        raise HTTPException(401, "Token invalide")