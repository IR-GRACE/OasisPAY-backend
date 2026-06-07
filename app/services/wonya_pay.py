import os
import httpx
import uuid
import re
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        self.callback_url = os.getenv("WONYA_CALLBACK_URL")
        self.base_url = "https://app-api.wonyasoft.com"
        if not all([self.api_key, self.project_ref, self.callback_url]):
            raise ValueError("WonyaPay credentials manquantes")

    def _normaliser_telephone(self, telephone: str) -> str:
        chiffres = re.sub(r'\D', '', telephone)
        if len(chiffres) == 9:
            return '243' + chiffres
        elif len(chiffres) == 10 and chiffres.startswith('0'):
            return '243' + chiffres[1:]
        elif len(chiffres) == 12 and chiffres.startswith('243'):
            return chiffres
        else:
            raise ValueError(f"Numéro invalide: {telephone}")

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, description: str) -> Dict[str, Any]:
        telephone_norm = self._normaliser_telephone(telephone)
        operateur = operateur.upper()
        mapping = {
            "AIRTEL": "AIRTEL MONEY",
            "ORANGE": "ORANGE MONEY",
            "VODACOM": "M-PESA"
        }
        mobilemoney = mapping.get(operateur, operateur)

        reference = f"OASIS_{uuid.uuid4().hex[:16].upper()}"
        payload = {
            "RefPartenaire": self.project_ref,
            "RefTransa": reference,
            "Action": "C2B",
            "Montant": round(float(montant), 2),
            "Devise": "CDF",
            "phone": telephone_norm,
            "mobilemoney": mobilemoney,
            "reference": reference,
            "description": description,
            "callback_url": self.callback_url
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        print(f"=== WONYAPAY: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payment", json=payload, headers=headers)
            print(f"Réponse: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"WonyaPay error: {response.text}")