import os
import httpx
import re
import uuid
from typing import Dict, Any

class WonyaPayService:
    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        self.callback_url = os.getenv("WONYA_CALLBACK_URL")
        self.base_url = "https://app-api.wonyasoft.com"
        if not all([self.api_key, self.project_ref, self.callback_url]):
            raise ValueError("Missing WonyaPay environment variables")

    def _generer_reference(self) -> str:
        return f"OASIS_{uuid.uuid4().hex[:16].upper()}"

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, description: str) -> Dict[str, Any]:
        # Nettoyer le numéro : ne garder que les chiffres
        chiffres = re.sub(r'\D', '', telephone)
        
        # Générer différentes variantes du numéro
        variantes_numero = set()
        if len(chiffres) == 9:
            variantes_numero.add(chiffres)                       # 994477720
            variantes_numero.add('0' + chiffres)                  # 0994477720
            variantes_numero.add('243' + chiffres)                # 243994477720
        elif len(chiffres) == 10 and chiffres.startswith('0'):
            variantes_numero.add(chiffres)                       # 0994477720
            variantes_numero.add(chiffres[1:])                    # 994477720
            variantes_numero.add('243' + chiffres[1:])            # 243994477720
        elif len(chiffres) == 12 and chiffres.startswith('243'):
            variantes_numero.add(chiffres)                       # 243994477720
            variantes_numero.add(chiffres[3:])                    # 994477720
            variantes_numero.add('0' + chiffres[3:])              # 0994477720
        else:
            variantes_numero.add(chiffres)
        
        base_operateur = operateur.upper()
        if 'ORANGE' in base_operateur:
            valeurs_mobile = ['ORANGE MONEY', 'ORANGE', 'OM', 'ORANGE_MONEY']
        elif 'AIRTEL' in base_operateur:
            valeurs_mobile = ['AIRTEL MONEY', 'AIRTEL', 'AM', 'AIRTEL_MONEY']
        elif 'VODA' in base_operateur or 'MPESA' in base_operateur:
            valeurs_mobile = ['M-PESA', 'MPESA', 'VODACOM', 'VODACOM MONEY']
        else:
            valeurs_mobile = [base_operateur, base_operateur.replace(' ', '')]

        reference = self._generer_reference()
        
        for phone_try in variantes_numero:
            for mobile_try in valeurs_mobile:
                payload = {
                    "RefPartenaire": self.project_ref,
                    "RefTransa": reference,
                    "Action": "C2B",
                    "Montant": round(float(montant), 2),
                    "Devise": "CDF",
                    "phone": phone_try,
                    "mobilemoney": mobile_try,
                    "reference": reference,
                    "description": description,
                    "callback_url": self.callback_url
                }
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                print(f"=== Essai: phone={phone_try}, mobilemoney={mobile_try}")
                async with httpx.AsyncClient() as client:
                    response = await client.post(f"{self.base_url}/payment", json=payload, headers=headers)
                    print(f"Status: {response.status_code}, Response: {response.text}")
                    if response.status_code == 200:
                        return response.json()
                    if "Unrecognized phone number prefix" not in response.text:
                        raise Exception(f"WonyaPay error: {response.text}")
        raise Exception("Aucune combinaison n'a fonctionné.")