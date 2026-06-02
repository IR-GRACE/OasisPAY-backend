import os
import httpx
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        self.base_url = "https://app-api.wonyasoft.com"

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        # Endpoint : à ajuster si besoin (/payment, /api/v1/payment, etc.)
        endpoint = f"{self.base_url}/payment"

        payload = {
            "token": self.api_key,
            "RefPartenaire": self.project_ref,
            "RefTransa": reference,           # ← Ajout de la référence transaction
            "amount": int(montant),
            "phone": telephone,
            "mobilemoney": operateur.upper(),
            "reference": reference,
            "description": description,
            "callback_url": os.getenv("WONYA_CALLBACK_URL")
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        print("=== DEBUG WONYA PAY ===")
        print(f"endpoint = {endpoint}")
        print(f"payload = {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(endpoint, json=payload, headers=headers)
            print(f"status_code = {response.status_code}")
            print(f"response text = {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur WonyaPay: {response.text}")