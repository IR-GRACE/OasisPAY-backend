import os
import secrets
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

DATABASE_URL = "postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway"
engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=['bcrypt'])

# Générer un api_key unique
api_key = secrets.token_urlsafe(32)
code_hash = pwd_context.hash('Grace1234')

print(f"API Key générée: {api_key[:20]}...")

with engine.connect() as conn:
    # Supprimer l'ancienne entrée
    conn.execute(text("DELETE FROM admin_users WHERE phone = '+243995030972'"))
    conn.commit()
    print('✅ Ancienne entrée supprimée')
    
    # Insérer GRACE avec api_key
    conn.execute(
        text("""
            INSERT INTO admin_users (name, phone, code_hash, api_key, is_active, created_at, updated_at)
            VALUES (:name, :phone, :code_hash, :api_key, :is_active, NOW(), NOW())
        """),
        {
            'name': 'GRACE Administrateur',
            'phone': '+243995030972',
            'code_hash': code_hash,
            'api_key': api_key,
            'is_active': True
        }
    )
    conn.commit()
    print('\n✅ GRACE inséré dans admin_users avec succès!')
    
    # Vérifier
    result = conn.execute(text("SELECT id, name, phone, is_active FROM admin_users WHERE phone = '+243995030972'"))
    row = result.fetchone()
    if row:
        print(f'   ID: {row[0]}, Nom: {row[1]}, Téléphone: {row[2]}, Actif: {row[3]}')
    else:
        print('   ⚠️ GRACE non trouvé')

print("\n✅ Terminé!")