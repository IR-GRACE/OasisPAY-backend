import os
import httpx
import hashlib
import hmac
import json
from datetime import datetime
from typing import Optional, Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY", "wpa_3w2dw0m48lek0ib4hfpt0fv3z8jrnpi9hxpbkddm8ysq3drsdn8")
        self.base_url = os.getenv("WONYA_BASE_URL", "https://dev.wonyasoft.com/projet-details/882816625142")
        self.project_ref = os.getenv("WONYA_PROJECT_REF", "882816625142")
        self.api_url = "https://app-api.wonyasoft.com"

    async def initier_paiement(
        self,
        montant: float,
        telephone: str,
        operateur: str,  # 'ORANGE', 'AIRTEL', 'MPESA'
        reference: str,
        description: str = "Frais scolaires OasisPAY"
    ) -> Dict[str, Any]:
        """Initie un paiement via WonyaPay"""
        async with httpx.AsyncClient() as client:
            payload = {
                "project_ref": self.project_ref,
                "amount": str(montant),
                "phone": telephone,
                "operator": operateur,
                "reference": reference,
                "description": description,
                "callback_url": os.getenv("WONYA_CALLBACK_URL", "https://oasispay-backend-production.up.railway.app/api/v1/paiements/webhook/wonya"),
            }
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
            response = await client.post(
                f"{self.api_url}/api/v1/payments/initiate",
                json=payload,
                headers=headers,
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur WonyaPay: {response.text}")

    async def verifier_statut(self, transaction_id: str) -> Dict[str, Any]:
        """Vérifie le statut d'une transaction"""
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            response = await client.get(
                f"{self.api_url}/api/v1/payments/status/{transaction_id}",
                headers=headers,
            )
            if response.status_code == 200:
                return response.json()
            raise Exception(f"Erreur vérification: {response.text}")

    def verifier_webhook(self, payload: bytes, signature: str) -> bool:
        """Vérifie la signature du webhook (si fournie)"""
        # À implémenter selon la doc WonyaPay
        return True
