from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

def create_user():
    db = SessionLocal()
    email = "stypojulvier009@gmail.com"
    password = "2003"
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                nom="Admin",
                prenom="System",
                hashed_password=get_password_hash(password),
                role="super_admin",
                actif=True
            )
            db.add(user)
            db.commit()
            print(f"✅ User {email} créé avec succès")
        else:
            print(f"ℹ️ L'User {email} existe déjà")
            # Mettre à jour le mot de passe si besoin
            user.hashed_password = get_password_hash(password)
            db.commit()
            print("Mot de passe mis à jour")
    except Exception as e:
        print(f"❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
