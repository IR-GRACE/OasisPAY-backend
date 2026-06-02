import os
from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Connexion PostgreSQL
DATABASE_URL = "postgresql://postgres:KdNPvevjoUfFtHEoKuSDQvejpYTtSiWg@monorail.proxy.rlwy.net:41061/railway"
engine = create_engine(DATABASE_URL)
pwd_context = CryptContext(schemes=['bcrypt'])

# Hasher le mot de passe
hashed_password = pwd_context.hash('Grace1234')
print("Mot de passe hashé généré")

with engine.connect() as conn:
    # 1. Supprimer GRACE de la table users s'il y est
    conn.execute(text("DELETE FROM users WHERE email = 'Masiyamulimbi4@gmail.com'"))
    conn.commit()
    print('✅ GRACE supprimé de users')
    
    # 2. Vérifier la structure de admin_users
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'admin_users'"))
    print('\n📋 Colonnes de admin_users:')
    columns = [row[0] for row in result]
    print(columns)
    
    # 3. Insérer GRACE dans admin_users
    conn.execute(
        text("""
            INSERT INTO admin_users (email, password_hash, full_name, role, is_active, created_at)
            VALUES (:email, :password_hash, :full_name, :role, :is_active, NOW())
            ON CONFLICT (email) DO UPDATE SET
                password_hash = EXCLUDED.password_hash,
                role = 'super_admin',
                is_active = True
        """),
        {
            'email': 'Masiyamulimbi4@gmail.com',
            'password_hash': hashed_password,
            'full_name': 'GRACE Administrateur',
            'role': 'super_admin',
            'is_active': True
        }
    )
    conn.commit()
    print('\n✅ GRACE inséré dans admin_users avec succès!')
    
    # 4. Vérifier
    result = conn.execute(text("SELECT id, email, role FROM admin_users WHERE email = 'Masiyamulimbi4@gmail.com'"))
    row = result.fetchone()
    if row:
        print(f'   ID: {row[0]}, Email: {row[1]}, Rôle: {row[2]}')
    else:
        print('   ⚠️ GRACE non trouvé')

print("\n✅ Terminé!")