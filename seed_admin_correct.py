import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

DATABASE_URL = "postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway"
engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=['bcrypt'])

# Hasher le mot de passe
code_hash = pwd_context.hash('Grace1234')
print("Code hash généré")

with engine.connect() as conn:
    # 1. Supprimer GRACE s'il existe déjà
    conn.execute(text("DELETE FROM admin_users WHERE phone = '+243995030972'"))
    conn.commit()
    print('✅ Ancienne entrée supprimée')
    
    # 2. Insérer GRACE dans admin_users avec la bonne structure
    conn.execute(
        text("""
            INSERT INTO admin_users (name, phone, code_hash, is_active, created_at)
            VALUES (:name, :phone, :code_hash, :is_active, NOW())
        """),
        {
            'name': 'GRACE Administrateur',
            'phone': '+243995030972',
            'code_hash': code_hash,
            'is_active': True
        }
    )
    conn.commit()
    print('\n✅ GRACE inséré dans admin_users avec succès!')
    
    # 3. Vérifier
    result = conn.execute(text("SELECT id, name, phone, is_active FROM admin_users WHERE phone = '+243995030972'"))
    row = result.fetchone()
    if row:
        print(f'   ID: {row[0]}, Nom: {row[1]}, Téléphone: {row[2]}, Actif: {row[3]}')
    else:
        print('   ⚠️ GRACE non trouvé')

print("\n✅ Terminé!")