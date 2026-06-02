import os
import httpx
import uuid
import re
from typing import Dict, Any

class FlutterwaveService:
    def __init__(self):
        self.secret_key = os.getenv("FLW_SECRET_KEY")
        self.base_url = "https://api.flutterwave.com/v3"
        if not self.secret_key:
            raise ValueError("FLW_SECRET_KEY manquante dans l'environnement")

    def _normaliser_telephone(self, telephone: str) -> str:
        """Convertit en format international 243XXXXXXXXX (12 chiffres)"""
        chiffres = re.sub(r'\D', '', telephone)
        if len(chiffres) == 9:
            return '243' + chiffres
        elif len(chiffres) == 10 and chiffres.startswith('0'):
            return '243' + chiffres[1:]
        elif len(chiffres) == 12 and chiffres.startswith('243'):
            return chiffres
        else:
            raise ValueError(f"Format de numéro invalide: {telephone}")

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, email: str, reference: str = None) -> Dict[str, Any]:
        telephone_norm = self._normaliser_telephone(telephone)
        operateur = operateur.upper()
        if operateur == "VODACOM":
            operateur_fw = "VODACOM"
        elif operateur == "ORANGE":
            operateur_fw = "ORANGE"
        elif operateur == "AIRTEL":
            operateur_fw = "AIRTEL"
        else:
            raise ValueError(f"Opérateur non supporté: {operateur}")

        if not reference:
            reference = f"OASIS_{uuid.uuid4().hex[:12].upper()}"

        payload = {
            "tx_ref": reference,
            "amount": round(float(montant), 2),
            "currency": "CDF",
            "phone_number": telephone_norm,
            "email": email,
            "fullname": "Client OasisPAY",
            "payment_type": "mobilemoney",
            "network": operateur_fw,
            "redirect_url": os.getenv("FLW_REDIRECT_URL", "https://oasispay-backend-production.up.railway.app/api/v1/paiements/webhook/flutterwave")
        }

        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }

        print(f"=== FLUTTERWAVE: {payload}")
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payments", json=payload, headers=headers)
            print(f"Status: {response.status_code}, Response: {response.text}")
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Flutterwave error: {response.text}")