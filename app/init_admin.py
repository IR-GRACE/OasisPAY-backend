import os
from sqlalchemy.orm import Session
from .database import SessionLocal, engine
from . import models
from .auth import get_password_hash

def init_admin():
    db = SessionLocal()
    try:
        admin_email = os.getenv("ADMIN_EMAIL", "stypojulvier009@mail.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "Mukend123")
        
        admin = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin:
            admin = models.User(
                nom="Administrateur",
                prenom="Principal",
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                role=models.RoleEnum.SUPER_ADMIN,
                actif=True,
                is_verified=True
            )
            db.add(admin)
            db.commit()
            print(f"✅ Super admin créé: {admin_email}")
        else:
            print(f"ℹ️ Super admin déjà existant: {admin_email}")
    except Exception as e:
        print(f"❌ Erreur initialisation admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_admin()
