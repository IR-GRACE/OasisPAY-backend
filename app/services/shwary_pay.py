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
        self.base_url = "https://api.shwary.com"
        if not self.merchant_id or not self.merchant_key:
            raise ValueError("Shwary credentials manquantes")

    def _normaliser_telephone(self, telephone: str) -> str:
        """Convertit en format E.164 (+243XXXXXXXXX)"""
        chiffres = re.sub(r'\D', '', telephone)
        if len(chiffres) == 9:
            return '+243' + chiffres
        elif len(chiffres) == 10 and chiffres.startswith('0'):
            return '+243' + chiffres[1:]
        elif len(chiffres) == 12 and chiffres.startswith('243'):
            return '+' + chiffres
        else:
            raise ValueError(f"Numéro invalide: {telephone}")

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, reference: str, description: str) -> Dict[str, Any]:
        telephone_norm = self._normaliser_telephone(telephone)
        
        # Montant minimum RDC = 2900 CDF
        montant_int = max(round(montant), 2900)
        
        # Pays : DRC (République Démocratique du Congo)
        country = "DRC"
        
        # Construction du payload selon la doc Shwary
        payload = {
            "amount": montant_int,
            "clientPhoneNumber": telephone_norm,
            "callbackUrl": os.getenv("SHWARY_CALLBACK_URL")
        }
        
        # En-tétes : x-merchant-id et x-merchant-key (pas Bearer)
        headers = {
            "x-merchant-id": self.merchant_id,
            "x-merchant-key": self.merchant_key,
            "Content-Type": "application/json"
        }
        
        # Choix de l'endpoint (sandbox ou production)
        if self.sandbox:
            endpoint = f"{self.base_url}/api/v1/merchants/payment/sandbox/{country}"
        else:
            endpoint = f"{self.base_url}/api/v1/merchants/payment/{country}"
        
        print(f"=== SHWARY PAYMENT (sandbox={self.sandbox}) ===")
        print(f"URL: {endpoint}")
        print(f"Payload: {payload}")
        print(f"Headers: x-merchant-id, x-merchant-key")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(endpoint, json=payload, headers=headers)
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                if response.status_code in (200, 201):
                    data = response.json()
                    # Extraire les informations importantes (reference = transactionId)
                    return {
                        "reference": data.get("referenceId") or data.get("id"),
                        "status": data.get("status"),
                        "transaction_id": data.get("id"),
                        "message": "Paiement initié avec succés"
                    }
                else:
                    raise Exception(f"Shwary error {response.status_code}: {response.text}")
            except Exception as e:
                raise Exception(f"Erreur de connexion Shwary: {str(e)}")