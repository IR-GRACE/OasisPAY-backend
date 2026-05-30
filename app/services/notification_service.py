﻿import httpx
import asyncio
import logging
from firebase_admin import messaging
from datetime import datetime
from app.core.config import settings
# Note: Vérifie tes chemins d'import, utilise la structure app.db
from app.db.session import SessionLocal
from app.db import models

logger = logging.getLogger("edupay.notifications")

class NotificationService:
    """Service de notifications (Push, Email, SMS)"""
    
    # Configuration via settings pour la sécurité
    BREVO_API_KEY = settings.admin_api_key  # À adapter dans config.py
    BREVO_API_URL = "https://api.brevo.com/v3"
    
    # Utilise des variables d'environnement pour ces clés !
    TERMII_API_KEY = getattr(settings, "termii_api_key", "PLACEHOLDER")
    TERMII_API_URL = "https://api.termii.com/api/sms/send"
    
    @classmethod
    async def send_push_notification(
        cls, 
        user_id: int | None = None, 
        token: str | None = None, 
        title: str = "", 
        body: str = "", 
        image_url: str | None = None,
        data: dict = None
    ):
        """Envoyer une notification push via Firebase.
        Accepte soit `user_id` (lira `fcm_token` depuis la BDD) soit `token` directement.
        """
        db = SessionLocal()
        try:
            fcm_token = token
            if not fcm_token:
                if not user_id:
                    return {"success": False, "error": "Aucun token ni user_id fourni"}
                # Adapté au modèle AdminUser ou Utilisateur selon ton cas
                user = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
                if not user or not user.fcm_token:
                    return {"success": False, "error": "Token FCM non trouvé"}
                fcm_token = user.fcm_token

            # Envoi réel via Firebase
            try:
                # Les valeurs dans 'data' doivent être des chaînes de caractères
                string_data = {k: str(v) for k, v in (data or {}).items()}
                
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title, 
                        body=body,
                        image=image_url
                    ),
                    data=string_data,
                    token=fcm_token,
                )
                await asyncio.to_thread(messaging.send, message)
            except messaging.UnregisteredError:
                # Le token n'est plus valide (application désinstallée ou token expiré)
                logger.warning(f"Token FCM non valide pour l'utilisateur {user_id}. Suppression du token...")
                if user_id:
                    user_to_clean = db.query(models.AdminUser).filter(models.AdminUser.id == user_id).first()
                    if user_to_clean:
                        user_to_clean.fcm_token = None
                        db.commit()
            except Exception as fcm_err:
                logger.error(f"Erreur lors de l'envoi FCM: {fcm_err}")

            # Sauvegarder dans la base
            notif = models.Notification(
                utilisateur_id=user_id,
                type="paiement",
                titre=title,
                message=body,
                data=data or {}
            )
            db.add(notif)
            db.commit()
            db.refresh(notif)

            return {"success": True, "notification_id": notif.id, "sent_to": fcm_token}
        finally:
            db.close()

    @classmethod
    def send_push_notification_sync(
        cls, 
        user_id: int | None = None, 
        token: str | None = None, 
        title: str = "", 
        body: str = "", 
        image_url: str | None = None,
        data: dict = None
    ):
        """Wrapper synchrone qui planifie ou exécute la coroutine d'envoi.
        Utilisez-le depuis des handlers synchrones ou BackgroundTasks.
        """
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        coro = cls.send_push_notification(
            user_id=user_id, 
            token=token, 
            title=title, 
            body=body, 
            image_url=image_url,
            data=data
        )
        if loop and loop.is_running():
            # schedule and return immediately
            loop.create_task(coro)
            return {"scheduled": True}
        else:
            # run until complete
            return asyncio.run(coro)
    
    @classmethod
    async def send_email(cls, to: str, subject: str, body: str):
        """Envoyer un email via Brevo"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{cls.BREVO_API_URL}/smtp/email",
                    headers={
                        "api-key": cls.BREVO_API_KEY,
                        "Content-Type": "application/json"
                    },
                    json={
                        "sender": {"email": "no-reply@oasispay.com", "name": "Oasis Pay"},
                        "to": [{"email": to}],
                        "subject": subject,
                        "htmlContent": body
                    }
                )
                logger.info(f"Email envoyé à {to}: {response.status_code}")
                return {"success": response.status_code == 201}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @classmethod
    async def send_sms(cls, phone: str, message: str):
        """Envoyer un SMS via Termii (Afrique)"""
        # Nettoyage du numéro pour le format international (ex DRC +243)
        clean_phone = phone.strip().replace(" ", "").replace("+", "")
        if clean_phone.startswith("0"):
            clean_phone = "243" + clean_phone[1:]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    cls.TERMII_API_URL,
                    json={
                        "to": clean_phone,
                        "from": "OasisPay",
                        "sms": message,
                        "type": "plain",
                        "channel": "generic",
                        "api_key": cls.TERMII_API_KEY
                    }
                )
                logger.info(f"SMS envoyé à {clean_phone}: {response.status_code}")
                return {"success": response.status_code == 200}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @classmethod
    async def notify_payment(cls, user_id: int, amount: float, reference: str):
        """Notifier un paiement réussi"""
        await cls.send_push_notification(
            user_id,
            "✅ Paiement réussi",
            f"Votre paiement de {amount} FC a été effectué. Réf: {reference}"
        )
    
    @classmethod
    async def notify_transfer(cls, user_id: int, amount: float, to_phone: str):
        """Notifier un transfert reçu"""
        await cls.send_push_notification(
            user_id,
            "💰 Transfert reçu",
            f"Vous avez reçu {amount} FC de {to_phone}"
        )
    
    @classmethod
    async def notify_admin_approval(cls, admin_id: int, user_name: str):
        """Notifier l'admin d'une nouvelle inscription"""
        await cls.send_push_notification(
            admin_id,
            "👤 Nouvelle inscription",
            f"{user_name} a créé un compte et attend votre validation."
        )
