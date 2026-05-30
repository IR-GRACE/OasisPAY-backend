#!/usr/bin/env python3
"""
Script pour ajouter GRACE comme Super Admin
À exécuter : python seed_grace.py
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db.models import User
from passlib.context import CryptContext
from sqlalchemy import text

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_grace_super_admin():
    db = SessionLocal()
    
    try:
        # Vérifier si GRACE existe déjà
        existing_user = db.query(User).filter(User.email == "Masiyamulimbi4@gmail.com").first()
        
        if existing_user:
            print(f"📝 GRACE existe déjà (ID: {existing_user.id})")
            print(f"   Email: {existing_user.email}")
            print(f"   Rôle actuel: {existing_user.role}")
            
            # Mettre à jour le mot de passe et le rôle
            existing_user.hashed_password = pwd_context.hash("Grace1234")
            existing_user.role = "super_admin"
            existing_user.actif = True
            existing_user.nom = "GRACE"
            existing_user.prenom = "Administrateur"
            existing_user.telephone = "+243995030972"
            existing_user.is_verified = True
            
            print("✅ Mise à jour effectuée avec succès!")
        else:
            print("✨ Création de GRACE comme Super Admin...")
            
            # Créer un nouvel utilisateur
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
            print("✅ GRACE a été créé avec succès!")
        
        db.commit()
        
        # Vérification finale
        grace = db.query(User).filter(User.email == "Masiyamulimbi4@gmail.com").first()
        print("\n📋 Informations de GRACE:")
        print(f"   ID: {grace.id}")
        print(f"   Email: {grace.email}")
        print(f"   Nom: {grace.nom}")
        print(f"   Rôle: {grace.role}")
        print(f"   Actif: {grace.actif}")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("Création de GRACE comme Super Admin")
    print("=" * 50)
    create_grace_super_admin()