import os
import sys
import asyncio

# Ajouter le chemin actuel pour pouvoir importer app
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/oasispay')

import requests
import json

async def create_grace():
    # Utiliser directement l'API au lieu de la DB
    url = "https://oasispay-backend-production.up.railway.app/api/v1/admin/create-super-admin"
    
    data = {
        "email": "Masiyamulimbi4@gmail.com",
        "password": "Grace1234",
        "nom": "GRACE",
        "prenom": "Administrateur",
        "telephone": "+243995030972",
        "role": "super_admin"
    }
    
    try:
        response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        print(f"Status: {response.status_code}")
        print(f"Réponse: {response.json()}")
        
        if response.status_code == 200:
            print("\n✅ GRACE a été créé avec succès!")
        else:
            print(f"\n❌ Erreur: {response.json().get('message', 'Inconnue')}")
            
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    asyncio.run(create_grace())