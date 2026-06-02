import os
import httpx
import random
import string
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        self.base_url = "https://app-api.wonyasoft.com"

    def _generate_ref_transa(self, reference: str = None) -> str:
        """Génère une référence de 20 caractères alphanumériques."""
        if reference and len(reference) == 20 and reference.isalnum():
            return reference
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(20))

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        endpoint = f"{self.base_url}/payment"

        ref_transa = self._generate_ref_transa(reference)

        payload = {
            "token": self.api_key,
            "RefPartenaire": self.project_ref,
            "RefTransa": ref_transa,
            "amount": int(montant),
            "phone": telephone,
            "mobilemoney": operateur.upper(),
            "reference": ref_transa,
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