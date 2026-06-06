from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from ..database import get_db
from ..models import Utilisateur
import os
import secrets
import smtplib
from email.message import EmailMessage

router = APIRouter(prefix="/auth", tags=["auth"])
SECRET_KEY = os.getenv("SECRET_KEY", "prod_secret_key_change_me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def verify_password(plain, hashed):
    # Désactivé pour la démo : on accepte n'importe quel mot de passe
    return True
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Token invalide")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise credentials_exception
    return user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == form_data.username).first()
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

@router.get("/me")
def get_me(current_user: Utilisateur = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "role": current_user.role,# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}


# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}
 
# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}
 
# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}
 
# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}
 
# ========== ENDPOINTS DE RÉINITIALISATION MOT DE PASSE ==========
# Stockage temporaire des tokens (à remplacer par Redis en production)
reset_tokens = {}

def send_reset_email(to_email: str, token: str):
    import smtplib
    from email.message import EmailMessage
    reset_link = f"https://oasispay-frontend.com/reset-password?token={token}"
    msg = EmailMessage()
    msg.set_content(f"Bonjour,\n\nCliquez sur le lien suivant pour réinitialiser votre mot de passe :\n{reset_link}\n\nSi vous n'êtes pas à l'origine de cette demande, ignorez cet email.")
    msg['Subject'] = "Réinitialisation de votre mot de passe OasisPAY"
    msg['From'] = os.getenv("SMTP_FROM_EMAIL", "noreply@oasispay.com")
    msg['To'] = to_email
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    if smtp_user and smtp_pass:
        with smtplib.SMTP(smtp_server, smtp_port) as smtp:
            smtp.starttls()
            smtp.login(smtp_user, smtp_pass)
            smtp.send_message(msg)

@router.post("/forgot-password")
def forgot_password(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email non trouvé")
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = email
    # Envoyer l'email en arrière-plan
    import threading
    threading.Thread(target=send_reset_email, args=(email, token)).start()
    return {"message": "Email de réinitialisation envoyé"}

@router.post("/reset-password")
def reset_password(token: str = Body(...), new_password: str = Body(...), db: Session = Depends(get_db)):
    email = reset_tokens.get(token)
    if not email:
        raise HTTPException(status_code=400, detail="Token invalide ou expiré")
    user = db.query(Utilisateur).filter(Utilisateur.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    del reset_tokens[token]
    return {"message": "Mot de passe modifié avec succès"}

# ========== MISE À JOUR DU PROFIL ==========
@router.put("/me")
def update_profile(
    nom: Optional[str] = Body(None),
    prenom: Optional[str] = Body(None),
    telephone: Optional[str] = Body(None),
    db: Session = Depends(get_db),
    current_user: Utilisateur = Depends(get_current_user)
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
        "role": current_user.role,}
}