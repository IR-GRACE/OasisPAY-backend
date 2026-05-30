from fastapi import APIRouter, Depends
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Header, Request
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth
import logging
from app.database import get_db
from app import models, auth
from app.services.payment_service import MobileMoneyService
from app.services.notification_service import NotificationService
from app.core.config import settings
import uuid

router = APIRouter(tags=["Paiements"])
logger = logging.getLogger("edupay.payments")

@router.get("/")
def get_payments(
@router.post("/initiate")
async def initiate_payment(
    amount: float,
    phone: str,
    provider: str,
    currency: str = "CDF",
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_user)
):
    return []
    """Route appelée par le frontend pour lancer un paiement"""
    reference = f"PAY-{uuid.uuid4().hex[:8].upper()}"
    
    # 1. Enregistrer la transaction en attente en BDD
    new_tx = models.Transaction(
        reference=reference,
        expediteur_id=current_user.id,
        montant=amount,
        total=amount, # Calculer les frais si nécessaire
        type="paiement",
        methode=provider,
        telephone=phone,
        statut=models.StatutPaiementEnum.EN_ATTENTE
    )
    db.add(new_tx)
    db.commit()

    # 2. Appeler le service de paiement réel
    result = await MobileMoneyService.process_payment(
        provider=provider,
        phone=phone,
        amount=amount,
        reference=reference,
        currency=currency
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result

@router.post("/webhook/flutterwave")
async def flutterwave_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    verif_hash: str = Header(None, alias="verif-hash")
):
    """Réception de la confirmation réelle de Flutterwave"""
    # Logique de vérification du hash et mise à jour BDD ici...
    # Une fois le paiement validé :
    # background_tasks.add_task(NotificationService.notify_payment, user_id, amount, ref)
    return {"status": "ok"}
