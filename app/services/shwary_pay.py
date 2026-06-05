import os
import httpx
import uuid
import re
from typing import Dict, Any

class ShwaryPayService:
    def __init__(self):
        self.merchant_id = os.getenv("SHWARY_MERCHANT_ID")
        self.merchant_key = os.getenv("SHWARY_MERCHANT_KEY")
        self.sandbox = os.getenv("SHWARY_SANDBOX", "true").lower() == "true"
        self.base_url = "https://api.shwary.com/v1" if not self.sandbox else "https://sandbox.shwary.com/v1"
        self.callback_url = os.getenv("SHWARY_CALLBACK_URL")
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

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str = None) -> Dict[str, Any]:
        telephone_norm = self._normaliser_telephone(telephone)
        operateur = operateur.upper()
        # Mapping Shwary (à adapter selon leur doc)
        if operateur == "ORANGE":
            provider = "ORANGE_MONEY"
        elif operateur == "AIRTEL":
            provider = "AIRTEL_MONEY"
        elif operateur == "VODACOM":
            provider = "M_PESA"
        else:
            provider = "ORANGE_MONEY"

        if not reference:
            reference = f"OASIS_{uuid.uuid4().hex[:12].upper()}"

        payload = {
            "merchant_id": self.merchant_id,
            "merchant_key": self.merchant_key,
            "amount": round(montant, 2),
            "currency": "CDF",
            "phone": telephone_norm,
            "provider": provider,
            "reference": reference,
            "callback_url": self.callback_url,
            "description": f"Paiement OasisPAY {reference}"
        }

        headers = {
            "Content-Type": "application/json"
        }

        print(f"=== Shwary Payment ===")
        print(f"endpoint: {self.base_url}/payment")
        print(f"payload: {payload}")

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payment", json=payload, headers=headers)
            print(f"status: {response.status_code}, response: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Shwary error: {response.text}")