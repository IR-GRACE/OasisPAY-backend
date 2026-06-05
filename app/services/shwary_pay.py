import os
import httpx
import uuid
import re
from typing import Dict, Any

class ShwaryService:
    def __init__(self):
        self.merchant_id = os.getenv("SHWARY_MERCHANT_ID")
        self.merchant_key = os.getenv("SHWARY_MERCHANT_KEY")
        self.sandbox = os.getenv("SHWARY_SANDBOX", "true") == "true"
        self.base_url = "https://api.shwary.com/v1" if not self.sandbox else "https://sandbox.api.shwary.com/v1"
        if not self.merchant_id or not self.merchant_key:
            raise ValueError("Shwary credentials manquantes")

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

    def _mapper_operateur(self, operateur: str) -> str:
        mapping = {
            "AIRTEL": "airtel",
            "ORANGE": "orange",
            "VODACOM": "vodacom"
        }
        return mapping.get(operateur.upper(), operateur.lower())

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        telephone_norm = self._normaliser_telephone(telephone)
        operateur_api = self._mapper_operateur(operateur)

        if not reference:
            reference = f"OASIS_{uuid.uuid4().hex[:12].upper()}"

        payload = {
            "merchant_id": self.merchant_id,
            "amount": round(montant, 2),
            "currency": "CDF",
            "phone": telephone_norm,
            "operator": operateur_api,
            "reference": reference,
            "description": description,
            "callback_url": os.getenv("SHWARY_CALLBACK_URL")
        }

        headers = {
            "Authorization": f"Bearer {self.merchant_key}",
            "Content-Type": "application/json"
        }

        print(f"=== SHWARY PAYMENT ===")
        print(f"Payload: {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payments", json=payload, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            if response.status_code == 200 or response.status_code == 201:
                return response.json()
            else:
                raise Exception(f"Shwary error: {response.text}")