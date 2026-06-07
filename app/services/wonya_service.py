import httpx
import random
import string
from typing import Optional

from app.core.config import settings

class WonyaPaymentService:
    DEFAULT_TIMEOUT = 30.0

    @staticmethod
    def generate_ref_transa() -> str:
        return "".join(random.choices(string.ascii_uppercase + string.digits, k=20))

    @staticmethod
    def build_payload(
        montant: float,
        reference: Optional[str] = None,
        currency: str = "CDF",
        mobilemoney: Optional[str] = None,
    ) -> dict:
        partner_ref = settings.wonya_partner_ref
        if not partner_ref:
            raise ValueError("Wonyapay partner reference not configured")

        if not reference or len(reference) != 20 or not reference.isalnum():
            reference = WonyaPaymentService.generate_ref_transa()

        mobilemoney = mobilemoney or settings.wonya_default_mobilemoney or "ORANGE"
        if not mobilemoney:
            raise ValueError("Wonyapay mobile money provider not configured")

        return {
            "RefPartenaire": partner_ref,
            "RefTransa": reference,
            "Montant": montant,
            "Devise": currency or "CDF",
            "Action": "C2B",
            "MobileMoney": mobilemoney,
            "mobilemoney": mobilemoney,
            "Motif": f"Paiement scolaire {reference}",
        }

    @staticmethod
    async def initier_paiement(
        telephone: Optional[str],
        montant: float,
        reference: Optional[str] = None,
        currency: str = "CDF",
        mobilemoney: Optional[str] = None,
    ):
        if not settings.wonya_api_key or not settings.wonya_base_url:
            return {"success": False, "error": "Wonyapay credentials not configured"}

        api_url = settings.wonya_api_url
        if not api_url:
            return {"success": False, "error": "Wonyapay API URL not configured"}

        try:
            payload = WonyaPaymentService.build_payload(montant, reference, currency, mobilemoney)
        except ValueError as exc:
            return {"success": False, "error": str(exc)}

        try:
            async with httpx.AsyncClient(timeout=WonyaPaymentService.DEFAULT_TIMEOUT) as client:
                resp = await client.post(
                    f"{api_url}/payment",
                    headers={
                        "Authorization": f"Bearer {settings.wonya_api_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                try:
                    data = resp.json()
                except ValueError:
                    data = resp.text

            if resp.status_code >= 400:
                return {"success": False, "status_code": resp.status_code, "error": data, "payload": payload}

            if isinstance(data, str) and "<html" in data.lower():
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "error": "Wonyapay a renvoyé une page HTML. Vérifie le `WONYA_BASE_URL` API.",
                    "data": data,
                    "payload": payload,
                }

            return {"success": True, "status_code": resp.status_code, "data": data, "payload": payload}
        except Exception as exc:
            return {"success": False, "error": str(exc), "payload": payload}

    @staticmethod
    async def verifier_statut(reference: str):
        if not settings.wonya_api_key or not settings.wonya_base_url:
            return {"success": False, "error": "Wonyapay credentials not configured"}

        api_url = settings.wonya_api_url
        if not api_url:
            return {"success": False, "error": "Wonyapay API URL not configured"}

        try:
            async with httpx.AsyncClient(timeout=WonyaPaymentService.DEFAULT_TIMEOUT) as client:
                resp = await client.get(
                    f"{api_url}/payment/{reference}",
                    headers={"Authorization": f"Bearer {settings.wonya_api_key}"},
                )
                try:
                    data = resp.json()
                except ValueError:
                    data = resp.text

            if resp.status_code >= 400:
                return {"success": False, "status_code": resp.status_code, "error": data}

            if isinstance(data, str) and "<html" in data.lower():
                return {
                    "success": False,
                    "status_code": resp.status_code,
                    "error": "Wonyapay a renvoyé une page HTML. Vérifie le `WONYA_BASE_URL` API.",
                    "data": data,
                }

            return {"success": True, "status_code": resp.status_code, "data": data}
        except Exception as exc:
            return {"success": False, "error": str(exc)}
