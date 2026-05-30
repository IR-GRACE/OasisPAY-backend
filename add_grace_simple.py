#!/usr/bin/env python3
"""
Script simple pour ajouter GRACE directement dans la base SQLite
"""

import sqlite3
import hashlib
import os
import binascii

def hash_password(password):
    """Hash un mot de passe avec salt"""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def add_grace_to_db():
    """Ajoute GRACE à la base de données"""
    print("AJOUT DE GRACE COMME SUPER ADMIN")
    print("="*50)
    
    # Informations de GRACE
    grace_info = {
        'name': 'GRACE',
        'phone': '+243995030972',
        'email': 'Masiyamulimbi4@gmail.com',
        'code': '2003',
        'api_key': 'supersecretadminkey'
    }
    
    try:
        # Connexion à la base SQLite
        conn = sqlite3.connect('edupay.db')
        cursor = conn.cursor()
        
        # Vérifie si la table admin_users existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("ERREUR: Table admin_users n'existe pas")
            print("Lance d'abord l'API pour créer les tables")
            return
        
        # Vérifie si GRACE existe déjà
        cursor.execute("SELECT id, name, phone FROM admin_users WHERE phone = ?", (grace_info['phone'],))
        existing = cursor.fetchone()
        
        if existing:
            print(f"GRACE existe déjà:")
            print(f"  ID: {existing[0]}")
            print(f"  Nom: {existing[1]}")
            print(f"  Telephone: {existing[2]}")
            
            # Met à jour
            update = input("Mettre à jour? (o/n): ").strip().lower()
            if update == 'o':
                # Hash du code
                code_hash = hash_password(grace_info['code'])
                cursor.execute("""
                    UPDATE admin_users 
                    SET name = ?, code_hash = ?, api_key = ?, is_active = 1
                    WHERE phone = ?
                """, (grace_info['name'], code_hash, grace_info['api_key'], grace_info['phone']))
                conn.commit()
                print("GRACE mis à jour avec succès")
        else:
            # Hash du code
            code_hash = hash_password(grace_info['code'])
            
            # Insère GRACE
            cursor.execute("""
                INSERT INTO admin_users (name, phone, code_hash, api_key, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, 1, datetime('now'), datetime('now'))
            """, (grace_info['name'], grace_info['phone'], code_hash, grace_info['api_key']))
            
            conn.commit()
            print("SUPER ADMIN GRACE AJOUTE AVEC SUCCES!")
            print(f"  Nom: {grace_info['name']}")
            print(f"  Telephone: {grace_info['phone']}")
            print(f"  Code: {grace_info['code']}")
            print(f"  API Key: {grace_info['api_key']}")
        
        # Vérifie aussi la table users pour JWT
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        users_table_exists = cursor.fetchone()
        
        if users_table_exists:
            # Vérifie si l'utilisateur existe
            cursor.execute("SELECT id, email FROM users WHERE email = ?", (grace_info['email'],))
            user_exists = cursor.fetchone()
            
            if not user_exists:
                # Crée l'utilisateur pour JWT
                cursor.execute("""
                    INSERT INTO users (email, full_name, role, status, is_active, created_at, updated_at)
                    VALUES (?, ?, 'super_admin', 'approved', 1, datetime('now'), datetime('now'))
                """, (grace_info['email'], grace_info['name']))
                conn.commit()
                print("UTILISATEUR GRACE CREE POUR AUTH JWT")
        
        # Liste tous les admins
        print("\n" + "="*50)
        print("LISTE DES ADMINISTRATEURS:")
        print("="*50)
        
        cursor.execute("SELECT id, name, phone, is_active FROM admin_users ORDER BY id")
        admins = cursor.fetchall()
        
        for admin in admins:
            status = "ACTIF" if admin[3] else "INACTIF"
            print(f"{admin[0]}. {admin[1]} - {admin[2]} [{status}]")
        
        conn.close()
        
        print("\n" + "="*50)
        print("INFORMATIONS DE CONNEXION:")
        print("="*50)
        print(f"Telephone: {grace_info['phone']}")
        print(f"Code: {grace_info['code']}")
        print(f"API Key: {grace_info['api_key']}")
        print(f"Email (JWT): {grace_info['email']}")
        
        print("\nTEST DE CONNEXION:")
        print(f"curl -X POST http://localhost:8000/api/admin/login \\")
        print(f"  -H \"Content-Type: application/json\" \\")
        print(f"  -d '{{\"phone\": \"{grace_info['phone']}\", \"code\": \"{grace_info['code']}\"}}'")
        
    except sqlite3.Error as e:
        print(f"ERREUR SQLite: {e}")
    except Exception as e:
        print(f"ERREUR: {e}")

if __name__ == "__main__":
    add_grace_to_db()