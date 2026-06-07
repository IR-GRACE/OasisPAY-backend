from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class InitiatePayment(BaseModel):
    etudiant_id: int = Field(..., description="Identifiant de l'étudiant")
    montant: float = Field(..., gt=0, description="Montant à payer")
    devise: str = Field("CDF", description="Devise du paiement")
    type_frais: Optional[str] = Field(None, description="Type de frais")
    methode_paiement: str = Field(..., description="Méthode: mpesa, orange ou airtel")
    numero_telephone: Optional[str] = Field(None, description="Numéro du payeur")


class PaymentResponse(BaseModel):
    id: int
    transaction_ref: str
    status: str
    provider: str
    message: str
    redirect_url: Optional[str] = None


class PaymentStatusResponse(BaseModel):
    transaction_ref: str
    status: str
    provider: str
    updated_at: datetime


class PaymentRead(BaseModel):
    id: int
    etudiant_id: int
    montant: float
    devise: str
    type_frais: Optional[str]
    methode_paiement: str
    provider: str
    numero_telephone: Optional[str]
    transaction_ref: str
    status: str
    provider_reference: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentWebhookPayload(BaseModel):
    transaction_ref: str
    status: str
    amount: Optional[float] = None
    phone_number: Optional[str] = None
    provider_reference: Optional[str] = None

    class Config:
        extra = "allow"
