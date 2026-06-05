import httpx
from typing import Optional

class NotificationService:
    @staticmethod
    async def send_push_notification(user_id: int, title: str, body: str):
        # À implémenter avec Firebase
        print(f"Push à l'utilisateur {user_id}: {title} - {body}")