import os
import httpx
import uuid
import re
from typing import Dict, Any

class WonyaPayService:
    # Opérateurs RDC officiels
    OPERATEURS_RDC = {
        "M-PESA": ["81", "82", "83"],
        "ORANGE MONEY": ["80", "84", "85", "88", "89"],
        "AIRTEL MONEY": ["97", "98", "99"],
        "AFRICELL": ["90", "91"]
    }

    def __init__(self):
        self.api_key = os.getenv("WONYA_API_KEY")
        self.project_ref = os.getenv("WONYA_PROJECT_REF")
        self.callback_url = os.getenv("WONYA_CALLBACK_URL")
        self.base_url = "https://app-api.wonyasoft.com"
        
        # Validation critique
        if not self.api_key:
            raise ValueError("WONYA_API_KEY manquante")
        if not self.project_ref:
            raise ValueError("WONYA_PROJECT_REF manquant")
        if not self.callback_url:
            raise ValueError("WONYA_CALLBACK_URL manquante")

    def normaliser_telephone(self, telephone: str) -> str:
        """Convertit en format 243XXXXXXXXX (validation stricte)"""
        numero = re.sub(r"\D", "", telephone)
        if numero.startswith("0"):
            numero = numero[1:]
        if not numero.startswith("243"):
            numero = "243" + numero
        if len(numero) != 12:
            raise ValueError(f"Format invalide : {numero} (doit faire 12 chiffres)")
        return numero

    def detecter_operateur(self, numero: str) -> str:
        """Détecte l'opérateur à partir du préfixe (positions 3-5)"""
        prefix = numero[3:5]
        for operateur, prefixes in self.OPERATEURS_RDC.items():
            if prefix in prefixes:
                return operateur
        raise ValueError(f"Préfixe non reconnu : {prefix} (numéro: {numero})")

    def generer_reference(self) -> str:
        """Génère une référence unique Oasis_XXXXXXXXXXXXXX"""
        return "OASIS_" + uuid.uuid4().hex[:16].upper()

    async def initier_paiement(self, montant: float, telephone: str, operateur: str, description: str) -> Dict[str, Any]:
        # Normalisation et validation
        telephone_normalise = self.normaliser_telephone(telephone)
        operateur_detecte = self.detecter_operateur(telephone_normalise)
        
        # Vérification cohérence opérateur
        if operateur and operateur.upper() != operateur_detecte.replace(" ", ""):
            raise ValueError(f"Le numéro {telephone} appartient à {operateur_detecte}, pas à {operateur}")
        
        reference = self.generer_reference()
        
        payload = {
            "RefPartenaire": self.project_ref,
            "RefTransa": reference,
            "Action": "C2B",
            "Montant": round(float(montant), 2),
            "Devise": "CDF",
            "phone": telephone_normalise,
            "mobilemoney": operateur_detecte,
            "reference": reference,
            "description": description,
            "callback_url": self.callback_url
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Logs détaillés
        print("===== WONYA DEBUG =====")
        print(f"Reference    : {reference}")
        print(f"Telephone    : {telephone_normalise}")
        print(f"Operateur    : {operateur_detecte}")
        print(f"Montant      : {round(montant, 2)}")
        print(f"Payload      : {payload}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/payment", json=payload, headers=headers)
            print(f"Status       : {response.status_code}")
            print(f"Response     : {response.text}")
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Erreur WonyaPay: {response.text}")