import os
import httpx
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.base_url = os.getenv("WONYA_BASE_URL")  # ex: https://dev.wonyasoft.com/projet-details/882816625142
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        # Utiliser l'URL de base du projet (sans /projet-details/...)
        # Si la base_url contient "/projet-details/", on extrait la partie API.
        if "/projet-details/" in self.base_url:
            self.api_url = "https://app-api.wonyasoft.com"
        else:
            self.api_url = self.base_url.rstrip('/')
        print(f"Using API URL: {self.api_url}")

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            # Endpoint exact selon la documentation WonyaPay (à vérifier)
            # Nous essayons d'abord /api/v1/payments/initiate
            endpoint = f"{self.api_url}/api/v1/payments/initiate"
            payload = {
                "project_ref": self.project_ref,
                "amount": str(montant),
                "phone": telephone,
                "operator": operateur,
                "reference": reference,
                "description": description,
                "callback_url": os.getenv("WONYA_CALLBACK_URL")
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            print(f"Calling WonyaPay: {endpoint}")
            print(f"Payload: {payload}")
            response = await client.post(endpoint, json=payload, headers=headers)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur WonyaPay: {response.text}")
