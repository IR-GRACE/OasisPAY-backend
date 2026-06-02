import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.db.models import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_grace():
    db = SessionLocal()
    
    try:
        # Vérifier si GRACE existe
        user = db.query(User).filter(User.email == "Masiyamulimbi4@gmail.com").first()
        
        if user:
            print(f"✏️  GRACE existe (ID: {user.id}) - Mise à jour...")
            user.hashed_password = pwd_context.hash("Grace1234")
            user.role = "super_admin"
            user.actif = True
            user.nom = "GRACE"
            user.prenom = "Administrateur"
            user.telephone = "+243995030972"
            user.is_verified = True
        else:
            print("✨ Création de GRACE...")
            new_user = User(
                email="Masiyamulimbi4@gmail.com",
                hashed_password=pwd_context.hash("Grace1234"),
                nom="GRACE",
                prenom="Administrateur",
                telephone="+243995030972",
                role="super_admin",
                actif=True,
                is_verified=True
            )
            db.add(new_user)
        
        db.commit()
        print("✅ Succès!")
        
        # Vérifier
        grace = db.query(User).filter(User.email == "Masiyamulimbi4@gmail.com").first()
        print(f"ID: {grace.id}, Email: {grace.email}, Rôle: {grace.role}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Création de GRACE comme Super Admin")
    print("=" * 50)
    create_grace()