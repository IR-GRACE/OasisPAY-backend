import os
import httpx
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        # URL de base de l'API (sans /payment)
        self.base_url = "https://app-api.wonyasoft.com"

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        # Endpoint à tester (plusieurs variantes possibles)
        # Variante 1 : /payment (simple)
        endpoint = f"{self.base_url}/payment"
        # Variante 2 : /api/v1/payment (décommentez pour tester)
        # endpoint = f"{self.base_url}/api/v1/payment"
        # Variante 3 : /mobile-money/payment
        # endpoint = f"{self.base_url}/mobile-money/payment"

        payload = {
            "token": self.api_key,
            "RefPartenaire": self.project_ref,   # ← clé corrigée
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

        # Logs de debug
        print("=== DEBUG WONYA PAY ===")
        print(f"project_ref = {self.project_ref}")
        print(f"api_key (masked) = {self.api_key[:10] if self.api_key else 'None'}...")
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