from fastapi import APIRouter, Depends, HTTPException, Request, BackgroundTasks, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from jose import JWTError, jwt
import bcrypt
import secrets
import os
from ..database import get_db
from ..models import User, UserSession, OtpCode
from ..utils.audit import log_audit
from ..services.email_service import send_email
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/auth", tags=["auth"])
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])

SECRET_KEY = os.getenv("SECRET_KEY", "prod_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

# ---------- Fonctions utilitaires ----------
def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_access_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire, "type": "access"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire, "type": "refresh"})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"

def get_user_agent(request: Request) -> str:
    return request.headers.get("user-agent", "")

# ---------- Dépendance d'authentification ----------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# ---------- Routes ----------

class RegisterRequest(BaseModel):
    nom: str
    prenom: str | None = None
    email: EmailStr
    telephone: str | None = None
    password: str
    role: str = "parent"

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):

    existing = db.query(User).filter(
        User.email == data.email
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email déjà utilisé"
        )

    user = User(
        nom=data.nom,
        prenom=data.prenom,
        email=data.email,
        telephone=data.telephone,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        actif=True,
        is_verified=True
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "email": user.email,
        "nom": user.nom,
        "role": user.role
    }

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        log_audit(db, None, "login_failed", ip=get_client_ip(request), ua=get_user_agent(request), status="failure")
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.actif:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh_token,
        user_agent=get_user_agent(request),
        ip_address=get_client_ip(request),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(session)
    db.commit()
    log_audit(db, user.id, "login_success", ip=get_client_ip(request), ua=get_user_agent(request))
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh")
def refresh(refresh_token: str = Form(...), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = int(payload.get("sub"))
        session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token, UserSession.revoked == False).first()
        if not session or session.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail="Session expired or revoked")
        session.revoked = True
        db.commit()
        new_access = create_access_token({"sub": str(user_id)})
        new_refresh = create_refresh_token({"sub": str(user_id)})
        new_session = UserSession(
            user_id=user_id,
            refresh_token=new_refresh,
            user_agent=session.user_agent,
            ip_address=session.ip_address,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(new_session)
        db.commit()
        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "bearer"}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
def logout(refresh_token: str, db: Session = Depends(get_db)):
    session = db.query(UserSession).filter(UserSession.refresh_token == refresh_token).first()
    if session:
        session.revoked = True
        db.commit()
    return {"msg": "Logged out"}

@router.post("/send-verification-email")
async def send_verification_email(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = secrets.token_urlsafe(32)
    otp = OtpCode(
        user_id=current_user.id,
        code=token,
        type="email",
        purpose="email_verification",
        expires_at=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    db.add(otp)
    db.commit()
    link = f"https://oasispay-backend-production.up.railway.app/api/v1/auth/verify-email?token={token}"
    await send_email(current_user.email, "Vérifiez votre adresse email", f"Cliquez sur ce lien : {link}", html=f"<a href='{link}'>Vérifier mon email</a>")
    return {"msg": "Email envoyé"}

@router.post("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    otp = db.query(OtpCode).filter(OtpCode.code == token, OtpCode.used == False, OtpCode.expires_at > datetime.now(timezone.utc)).first()
    if not otp:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(User).filter(User.id == otp.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.is_verified = True
    otp.used = True
    db.commit()
    return {"msg": "Email vérifié avec succès"}


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "admin_ecole", "directeur"]:
        raise HTTPException(
            status_code=403,
            detail="Droits administrateur requis"
        )
    return current_user

