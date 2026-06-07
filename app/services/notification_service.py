import httpx
from typing import Optional

class NotificationService:
    @staticmethod
    async def send_push_notification(user_id: int, title: str, body: str):
        # é implémenter avec Firebase
        print(f"Push é l'User {user_id}: {title} - {body}")