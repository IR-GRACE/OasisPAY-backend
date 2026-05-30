import httpx
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYAPAY_API_KEY")
        self.base_url = os.getenv("WONYAPAY_BASE_URL")
        self.merchant_id = os.getenv("WONYAPAY_MERCHANT_ID", "OasisPAY_001")
    
    async def initier_paiement(
        self,
        montant: float,
        telephone: str,
        operateur: str,
        reference: str,
        description: str = "Paiement scolaire OasisPAY"
    ) -> Dict[str, Any]:
        """Initier un paiement via WonyaPay"""
        async with httpx.AsyncClient() as client:
            payload = {
                "api_key": self.api_key,
                "merchant_id": self.merchant_id,
                "amount": montant,
                "phone": telephone,
                "operator": operateur,  # ORANGE, AIRTEL, VODACOM
                "reference": reference,
                "description": description,
                "callback_url": "https://oasispay-api.onrender.com/api/v1/paiements/webhook/wonyapay"
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/payment/initiate",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"WonyaPay error: {response.text}")
    
    async def verifier_statut(self, transaction_id: str) -> Dict[str, Any]:
        """Vérifier le statut d'une transaction"""
        async with httpx.AsyncClient() as client:
            payload = {
                "api_key": self.api_key,
                "transaction_id": transaction_id
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/payment/status",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"WonyaPay error: {response.text}")
    
    async def annuler_paiement(self, transaction_id: str) -> Dict[str, Any]:
        """Annuler un paiement"""
        async with httpx.AsyncClient() as client:
            payload = {
                "api_key": self.api_key,
                "transaction_id": transaction_id
            }
            
            response = await client.post(
                f"{self.base_url}/api/v1/payment/cancel",
                json=payload,
                timeout=30.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"WonyaPay error: {response.text}")

wonyapay_service = WonyaPayService()
