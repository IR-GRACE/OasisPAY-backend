import json
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import decode_access_token
from app.db.models import Payment, User
from app.db.session import get_db
from app.schemas.payment import PaymentRead
from app.schemas.user import UserRead
from app.services.payment_service import MobileMoneyService
from app.services.wonya_service import WonyaPaymentService

router = APIRouter()


def _get_current_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token d'accès manquant")
    token = authorization.split(" ", 1)[1]
    try:
        claims = decode_access_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    user = db.query(User).filter(User.email == claims.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User introuvable ou inactif")
    return user


@router.get("/etudiants/verifier/{matricule}")
async def verify_matricule(matricule: str, current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    student = db.query(User).filter(User.student_id == matricule, User.role == "student").first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matricule introuvable")
    return UserRead.from_orm(student)


@router.get("/etudiants/", response_model=list[UserRead])
async def list_etudiants(current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "student").all()
    return [UserRead.from_orm(student) for student in students]


@router.get("/parents/mes-enfants", response_model=list[UserRead])
async def get_parent_children(current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    students = db.query(User).filter(User.role == "student", User.status == "approved").all()
    return [UserRead.from_orm(student) for student in students]


@router.get("/paiements/", response_model=list[PaymentRead])
async def list_paiements(current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    payments = db.query(Payment).all()
    return payments


@router.post("/paiements/wonya/test")
async def test_wonya_paiement(request: Request, current_user: User = Depends(_get_current_user)):
    body = await request.json()
    montant = float(body.get("montant", 0.0))
    currency = body.get("devise", "CDF")
    mobilemoney = body.get("mobilemoney") or body.get("reseau") or body.get("network")
    reference = body.get("transaction_ref") or body.get("RefTransa")
    execute = bool(body.get("execute", False))

    try:
        payload = WonyaPaymentService.build_payload(montant, reference, currency, mobilemoney)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    response = {
        "success": True,
        "api_url": settings.wonya_api_url,
        "partner_ref": settings.wonya_partner_ref,
        "payload": payload,
    }

    if execute:
        result = await WonyaPaymentService.initier_paiement(
            None,
            montant,
            payload["RefTransa"],
            currency,
            payload["MobileMoney"],
        )
        response["result"] = result

    return response


@router.post("/paiements/", response_model=PaymentRead)
async def create_paiement(request: Request, current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    body = await request.json()
    transaction_ref = body.get("transaction_ref") or f"MANUAL_{uuid.uuid4().hex[:16]}"
    provider = (body.get("provider") or body.get("methode_paiement", "manual")).lower()
    montant = float(body.get("montant", 0.0))
    payment_status = body.get("status", "pending")
    provider_reference = body.get("provider_reference")
    raw_payload = json.dumps(body, ensure_ascii=False)

    if provider != "manual":
        mobilemoney = body.get("mobilemoney") or body.get("reseau") or body.get("network")
        numero_telephone = body.get("numero_telephone")
        if provider != "wonya" and not numero_telephone:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le numéro de téléphone est requis pour les paiements mobiles")

        result = await MobileMoneyService.process_payment(
            provider,
            numero_telephone,
            montant,
            transaction_ref,
            currency=body.get("devise"),
            mobilemoney=mobilemoney,
        )

        payment_status = "pending" if result.get("success") else "failed"
        raw_payload = json.dumps(result, ensure_ascii=False)

        if isinstance(result.get("data"), dict):
            provider_reference = (
                result["data"].get("provider_reference")
                or result["data"].get("reference")
                or result["data"].get("tx_ref")
                or result["data"].get("transaction_id")
                or result["data"].get("id")
                or result["data"].get("RefTransa")
                or result["data"].get("transactionId")
            )

    payment = Payment(
        etudiant_id=int(body.get("etudiant_id", 0)),
        montant=montant,
        devise=body.get("devise", "CDF"),
        type_frais=body.get("type_frais"),
        methode_paiement=body.get("methode_paiement", "manual"),
        provider=provider,
        numero_telephone=body.get("numero_telephone"),
        transaction_ref=transaction_ref,
        status=payment_status,
        provider_reference=provider_reference,
        raw_payload=raw_payload,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


@router.get("/paiements/ref/{transaction_ref}", response_model=PaymentRead)
async def paiement_by_ref(transaction_ref: str, current_user: User = Depends(_get_current_user), db: Session = Depends(get_db)):
    payment = db.query(Payment).filter(Payment.transaction_ref == transaction_ref).first()
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paiement introuvable")
    return payment
