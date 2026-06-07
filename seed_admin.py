import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

DATABASE_URL = "postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway"
engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=['bcrypt'])

# Mot de passe "Grace1234"
hashed_password = pwd_context.hash('Grace1234')
email = 'Masiyamulimbi4@gmail.com'

with engine.connect() as conn:
    # Supprimer l'ancien enregistrement (s'il existe)
    conn.execute(text("DELETE FROM utilisateurs WHERE email = :email"), {'email': email})
    conn.commit()
    print(f'✅ Ancien compte supprimé pour {email}')

    # Insérer dans la table utilisateurs (selon ton modèle SQLAlchemy)
    conn.execute(
        text("""
            INSERT INTO utilisateurs (email, nom, prenom, telephone, hashed_password, role, actif, is_verified)
            VALUES (:email, :nom, :prenom, :telephone, :hashed_password, :role, :actif, :is_verified)
        """),
        {
            'email': email,
            'nom': 'Masiya',
            'prenom': 'Mulimbi',
            'telephone': '0992494226',
            'hashed_password': hashed_password,
            'role': 'super_admin',
            'actif': True,
            'is_verified': True
        }
    )
    conn.commit()
    print(f'✅ Compte GRACE inséré avec succès dans utilisateurs')

    # Vérification
    result = conn.execute(text("SELECT id, email, role FROM utilisateurs WHERE email = :email"), {'email': email})
    row = result.fetchone()
    if row:
        print(f'   ID: {row[0]}, Email: {row[1]}, Rôle: {row[2]}')
    else:
        print('⚠️ ERREUR : compte non trouvé')

print("\n✅ Terminé !")