#!/usr/bin/env python3
"""
Ajout du SUPER ADMIN GRACE
Téléphone: +243 995 030 972
Email: Masiyamulimbi4@gmail.com
Mot de passe: 2003
"""

import sys
import os
from pathlib import Path

# Ajoute le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import AdminUser, User
from app.core.security import hash_secret
from app.core.config import settings

def create_super_admin_grace():
    """Crée le super admin GRACE"""
    print("="*60)
    print("AJOUT DU SUPER ADMIN GRACE")
    print("="*60)
    
    # Informations du super admin
    admin_info = {
        "name": "GRACE",
        "phone": "+243995030972",  # Format sans espaces
        "email": "Masiyamulimbi4@gmail.com",
        "code": "2003",
        "role": "super_admin"
    }
    
    print(f"\n📋 Informations admin :")
    print(f"   • Nom : {admin_info['name']}")
    print(f"   • Téléphone : {admin_info['phone']}")
    print(f"   • Email : {admin_info['email']}")
    print(f"   • Code : {admin_info['code']}")
    print(f"   • Rôle : {admin_info['role']}")
    
    db = SessionLocal()
    try:
        # Vérifie si l'admin existe déjà
        existing_admin = db.query(AdminUser).filter(
            (AdminUser.phone == admin_info['phone']) | 
            (AdminUser.name == admin_info['name'])
        ).first()
        
        if existing_admin:
            print(f"\n⚠️  Admin existe déjà :")
            print(f"   • ID : {existing_admin.id}")
            print(f"   • Nom : {existing_admin.name}")
            print(f"   • Téléphone : {existing_admin.phone}")
            print(f"   • Actif : {existing_admin.is_active}")
            
            # Met à jour si nécessaire
            update = input("\n🎯 Mettre à jour ? (o/n) : ").strip().lower()
            if update == 'o':
                existing_admin.name = admin_info['name']
                existing_admin.code_hash = hash_secret(admin_info['code'])
                existing_admin.is_active = True
                db.commit()
                print("✅ Admin mis à jour")
            else:
                print("❌ Annulé")
                return
        else:
            # Crée le nouvel admin
            new_admin = AdminUser(
                name=admin_info['name'],
                phone=admin_info['phone'],
                code_hash=hash_secret(admin_info['code']),
                api_key=settings.admin_api_key,  # Utilise la même clé API
                is_active=True
            )
            
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            
            print(f"\n✅ SUPER ADMIN CRÉÉ AVEC SUCCÈS !")
            print(f"   • ID : {new_admin.id}")
            print(f"   • Nom : {new_admin.name}")
            print(f"   • Téléphone : {new_admin.phone}")
            print(f"   • Date création : {new_admin.created_at}")
        
        # Crée aussi un User User pour l'authentification JWT
        create_user_for_admin(admin_info, db)
        
        print("\n" + "="*60)
        print("🎯 INFORMATIONS DE CONNEXION :")
        print("="*60)
        print(f"\n1. Login admin :")
        print(f"   URL : POST http://localhost:8000/api/admin/login")
        print(f"   Body : {{")
        print(f"     \"phone\": \"{admin_info['phone']}\",")
        print(f"     \"code\": \"{admin_info['code']}\"")
        print(f"   }}")
        
        print(f"\n2. Clé API pour les routes admin :")
        print(f"   X-API-KEY: {settings.admin_api_key}")
        
        print(f"\n3. Routes accessibles :")
        print(f"   • GET  /api/admin/paiements/pending")
        print(f"   • GET  /api/admin/paiements/{{id}}")
        print(f"   • POST /api/admin/paiements/{{id}}/status")
        print(f"   • GET  /api/admin/utilisateurs/pending")
        print(f"   • POST /api/admin/utilisateurs")
        print(f"   • POST /api/admin/utilisateurs/{{id}}/approve")
        print(f"   • PUT  /api/admin/utilisateurs/{{id}}")
        print(f"   • DELETE /api/admin/utilisateurs/{{id}}")
        print(f"   • GET  /api/admin/admins")
        print(f"   • POST /api/admin/admins")
        print(f"   • PUT  /api/admin/admins/{{id}}")
        print(f"   • DELETE /api/admin/admins/{{id}}")
        print(f"   • GET  /api/admin/audit")
        
        print(f"\n4. Test immédiat :")
        print(f"   curl -X POST http://localhost:8000/api/admin/login \\")
        print(f"     -H \"Content-Type: application/json\" \\")
        print(f"     -d '{{\"phone\": \"{admin_info['phone']}\", \"code\": \"{admin_info['code']}\"}}'")
        
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()

def create_user_for_admin(admin_info, db):
    """Crée un User User pour l'authentification JWT"""
    print(f"\n👤 Création User pour authentification JWT...")
    
    # Vérifie si l'User existe déjà
    existing_user = db.query(User).filter(
        User.email == admin_info['email']
    ).first()
    
    if existing_user:
        print(f"   ⚠️  User existe déjà : {existing_user.email}")
        # Met à jour le rôle
        existing_user.role = admin_info['role']
        existing_user.full_name = admin_info['name']
        existing_user.is_active = True
        db.commit()
        print(f"   ✅ Rôle mis à jour : {admin_info['role']}")
    else:
        # Crée un nouvel User
        new_user = User(
            email=admin_info['email'],
            full_name=admin_info['name'],
            role=admin_info['role'],
            status="approved",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"   ✅ User créé : {new_user.email} ({new_user.role})")
    
    print(f"\n🔐 Authentification JWT disponible :")
    print(f"   • Email : {admin_info['email']}")
    print(f"   • Rôle : {admin_info['role']}")
    print(f"   • Token : Via /api/auth/login")

def test_admin_login():
    """Teste la connexion du super admin"""
    print("\n" + "="*60)
    print("🧪 TEST DE CONNEXION SUPER ADMIN")
    print("="*60)
    
    import requests
    
    test_data = {
        "phone": "+243995030972",
        "code": "2003"
    }
    
    print(f"\nTest login avec :")
    print(f"   • Téléphone : {test_data['phone']}")
    print(f"   • Code : {test_data['code']}")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/admin/login",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ CONNEXION RÉUSSIE !")
            print(f"   • Statut : {response.status_code}")
            print(f"   • Message : {result.get('message', 'N/A')}")
            print(f"   • API Key : {result.get('api_key', 'N/A')}")
            
            if 'api_key' in result:
                print(f"\n🎯 Test routes admin avec cette clé :")
                print(f"   curl -H \"X-API-KEY: {result['api_key']}\" \\")
                print(f"     http://localhost:8000/api/admin/paiements/pending")
        else:
            print(f"\n❌ Échec connexion : {response.status_code}")
            print(f"   Réponse : {response.text}")
            
    except Exception as e:
        print(f"\n❌ Erreur test : {e}")
        print(f"   Vérifie que l'API est en cours d'exécution")

def list_all_admins():
    """Liste tous les administrateurs"""
    print("\n" + "="*60)
    print("📋 LISTE DES ADMINISTRATEURS")
    print("="*60)
    
    db = SessionLocal()
    try:
        admins = db.query(AdminUser).all()
        
        if not admins:
            print("   Aucun administrateur trouvé")
        else:
            print(f"\nTotal : {len(admins)} administrateur(s)")
            for i, admin in enumerate(admins, 1):
                print(f"\n{i}. {admin.name}")
                print(f"   • ID : {admin.id}")
                print(f"   • Téléphone : {admin.phone}")
                print(f"   • Actif : {admin.is_active}")
                print(f"   • Créé le : {admin.created_at}")
                
    except Exception as e:
        print(f"❌ Erreur : {e}")
    finally:
        db.close()

def main():
    print("🚀 AJOUT SUPER ADMIN - EDUPAY")
    print("="*60)
    
    # Vérifie que la base de données existe
    db_path = Path("edupay.db")
    if not db_path.exists():
        print("❌ Base de données non trouvée")
        print("🔧 Lance d'abord l'API pour créer la base :")
        print("   uvicorn app.main:app --reload")
        return
    
    print("\nChoisis une action :")
    print("1. Ajouter le super admin GRACE")
    print("2. Tester la connexion")
    print("3. Lister tous les admins")
    print("4. Tout faire")
    
    choice = input("\n🎯 Ton choix (1-4) : ").strip()
    
    if choice in ["1", "4"]:
        create_super_admin_grace()
    
    if choice in ["2", "4"]:
        test_admin_login()
    
    if choice in ["3", "4"]:
        list_all_admins()
    
    print("\n" + "="*60)
    print("🎉 CONFIGURATION TERMINÉE !")
    print("="*60)
    
    print("\n📞 Contacts admin :")
    print("1. GRACE (Super Admin)")
    print("   • Téléphone : +243 995 030 972")
    print("   • Email : Masiyamulimbi4@gmail.com")
    print("   • Code : 2003")
    
    print("\n2. JULVIER (Admin existant)")
    print("   • Téléphone : 0994477720")
    print("   • Code : 2003")
    
    print("\n🔐 Clé API admin :")
    print(f"   {settings.admin_api_key}")
    
    print("\n🌐 URLs importantes :")
    print("   • API : http://localhost:8000")
    print("   • Docs : http://localhost:8000/docs")
    print("   • Health : http://localhost:8000/health")
    
    print("\n🔥 Tu es prêt à gérer ton système avec GRACE comme super admin !")

if __name__ == "__main__":
    main()