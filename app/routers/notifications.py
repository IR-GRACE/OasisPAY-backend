from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth
from ..services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/register-token")
def register_fcm_token(
    token: str,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.get_current_user)
):
    """Enregistrer le token FCM du mobile"""
    current_user.fcm_token = token
    db.commit()
    return {"success": True, "message": "Token enregistré"}

@router.post("/send-test")
def send_test_notification(
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_super_admin)
):
    """Tester l'envoi de notification"""
    result = NotificationService.send_test_notification()
    return result

@router.post("/send")
def send_notification(
    user_id: int,
    title: str,
    body: str,
    db: Session = Depends(get_db),
    current_user: models.Utilisateur = Depends(auth.require_super_admin)
):
    """Envoyer une notification à un utilisateur"""
    user = db.query(models.Utilisateur).filter(models.Utilisateur.id == user_id).first()
    if not user or not user.fcm_token:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    result = NotificationService.send_push_notification(
        token=user.fcm_token,
        title=title,
        body=body
    )
    return result
