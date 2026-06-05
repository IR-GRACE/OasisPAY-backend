import httpx
import json
import uuid
import base64
import asyncio
from datetime import datetime
from typing import Optional

from ..core.config import settings
from .wonya_service import WonyaPaymentService


class MobileMoneyService:
    """Service de paiement mobile qui utilise les configurations dans `settings`.

    Implémente des appels réels (MPESA, Flutterwave). Les clés et endpoints
    doivent être fournis via les variables d'environnement / `Settings`.
    """

    DEFAULT_TIMEOUT = 30.0
    MAX_RETRIES = 3

    @classmethod
    async def _request_with_retries(cls, method: str, url: str, **kwargs):
        last_exc = None
        for attempt in range(1, cls.MAX_RETRIES + 1):
            try:
                async with httpx.AsyncClient(timeout=cls.DEFAULT_TIMEOUT) as client:
                    resp = await client.request(method, url, **kwargs)
                    try:
                        data = resp.json()
                    except Exception:
                        data = resp.text
                    if resp.status_code >= 400:
                        raise httpx.HTTPStatusError(f"{resp.status_code} - {data}", request=resp.request, response=resp)
                    return {"success": True, "status_code": resp.status_code, "data": data}
            except Exception as e:
                last_exc = e
                backoff = 0.5 * attempt
                await asyncio.sleep(backoff)
        return {"success": False, "error": str(last_exc)}

    @classmethod
    async def process_mpesa_payment(cls, phone: str, amount: float, reference: str):
        """Effectue un STK Push (CustomerPayBillOnline) vers l'API M-Pesa.

        Nécessite dans `settings`: `mpesa_consumer_key`, `mpesa_consumer_secret`,
        `mpesa_shortcode`, `mpesa_passkey`, et `mpesa_api_url` (optionnel).
        """
        # Configuration
        consumer_key = settings.mpesa_consumer_key
        consumer_secret = settings.mpesa_consumer_secret
        shortcode = settings.mpesa_shortcode
        passkey = settings.mpesa_passkey
        stk_url = getattr(settings, "mpesa_api_url", "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest")

        if not all([consumer_key, consumer_secret, shortcode, passkey]):
            return {"success": False, "error": "MPESA credentials not configured"}

        # 1) Get OAuth token
        token_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        auth = (consumer_key, consumer_secret)
        token_resp = await cls._request_with_retries("GET", token_url, auth=auth)
        if not token_resp.get("success"):
            return {"success": False, "error": f"OTP token error: {token_resp.get('error')}"}
        token_data = token_resp.get("data")
        access_token = token_data.get("access_token") if isinstance(token_data, dict) else None
        if not access_token:
            return {"success": False, "error": "Failed to obtain mpesa access token"}

        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(f"{shortcode}{passkey}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": shortcode,
            "PhoneNumber": phone,
            "CallBackURL": settings.webhook_base_url or "https://example.com/mpesa/callback",
            "AccountReference": reference,
            "TransactionDesc": "Paiement"
        }

        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
        return await cls._request_with_retries("POST", stk_url, json=payload, headers=headers)

    @classmethod
    async def process_flutterwave_payment(cls, phone: str, amount: float, reference: str, currency: str = None):
        """Effectue un paiement via Flutterwave `charges` endpoint en utilisant la clé secrète.

        Nécessite `flutterwave_secret_key` et `flutterwave_base_url` dans `settings`.
        Ce méthode initie une charge et retourne la réponse complète de Flutterwave.
        """
        secret = settings.flutterwave_secret_key
        base = settings.flutterwave_base_url or "https://api.flutterwave.com/v3"
        if not secret:
            return {"success": False, "error": "Flutterwave secret key not configured"}

        tx_ref = reference or str(uuid.uuid4())
        payload = {
            "tx_ref": tx_ref,
            "amount": str(amount),
            "currency": currency or settings.flutterwave_country or "CDF",
            "redirect_url": settings.webhook_base_url or "https://example.com/flutterwave/callback",
            "customer": {"phone_number": phone},
            "meta": {"reference": reference}
        }

        headers = {"Authorization": f"Bearer {secret}", "Content-Type": "application/json"}
        return await cls._request_with_retries("POST", f"{base}/payments", json=payload, headers=headers)

    @classmethod
    async def process_payment(cls, provider: str, phone: str, amount: float, reference: str, **kwargs):
        provider = provider.lower()
        if provider == "mpesa":
            return await cls.process_mpesa_payment(phone, amount, reference)
        if provider == "flutterwave":
            return await cls.process_flutterwave_payment(phone, amount, reference, kwargs.get("currency"))
        if provider.startswith("wonya"):
            mobilemoney = kwargs.get("mobilemoney") or kwargs.get("network") or kwargs.get("reseau")
            if provider != "wonya" and provider.startswith("wonya_"):
                mobilemoney = mobilemoney or provider.split("_", 1)[1]
            return await cls.process_wonya_payment(phone, amount, reference, kwargs.get("currency"), mobilemoney)
        # fallback: unimplemented providers
        return {"success": False, "error": f"Provider '{provider}' not implemented"}

    @classmethod
    async def process_wonya_payment(cls, phone: str, amount: float, reference: str, currency: str = None, mobilemoney: Optional[str] = None):
        return await WonyaPaymentService.initier_paiement(phone, amount, reference, currency, mobilemoney)
