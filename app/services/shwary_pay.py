import os
import httpx
import uuid
import re
from typing import Dict, Any

class ShwaryService:
    def __init__(self):
        self.merchant_id = os.getenv("SHWARY_MERCHANT_ID")
        self.merchant_key = os.getenv("SHWARY_MERCHANT_KEY")
        self.base_url = "https://api.shwary.com"
        if not self.merchant_id or not self.merchant_key:
            raise ValueError("Shwary credentials manquantes")

    def _normaliser_telephone(self, telephone: str) -> str:
        chiffres = re.sub(r'\D', '', telephone)
        if len(chiffres) == 9:
            return '+243' + chiffres
        elif len(chiffres) == 10 and chiffres.startswith('0'):
            return '+243' + chiffres[1:]
        elif len(chiffres) == 12 and chiffres.startswith('243'):
            return '+' + chiffres
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

        # Liste des endpoints probables (ordre à essayer)
        endpoints = [
            "/v1/payment/initiate",
            "/payment/initiate",
            "/payment",
            "/api/payment",
            "/v1/payment"
        ]

        headers = {
            "Authorization": f"Bearer {self.merchant_key}",
            "Content-Type": "application/json"
        }

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

        last_error = None
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            print(f"Tentative endpoint: {url}")
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(url, json=payload, headers=headers)
                    print(f"Status: {response.status_code}, Response: {response.text}")
                    if response.status_code in (200, 201):
                        return response.json()
                    else:
                        last_error = f"{url} -> {response.status_code}: {response.text}"
                except Exception as e:
                    last_error = f"{url} -> Exception: {str(e)}"
        raise Exception(f"Aucun endpoint n'a fonctionné. Dernière erreur: {last_error}")