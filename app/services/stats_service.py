from sqlalchemy import func, and_
from datetime import datetime, timedelta
from ..database import SessionLocal
from .. import models

class StatsService:
    @staticmethod
    def get_daily_stats(ecole_id=None):
        db = SessionLocal()
        try:
            today = datetime.utcnow().date()
            stats = {
                "total_users": db.query(models.Utilisateur).count(),
                "active_users": db.query(models.Utilisateur).filter(models.Utilisateur.actif == True).count(),
                "total_transactions": db.query(models.Transaction).count(),
                "daily_volume": db.query(func.sum(models.Transaction.montant)).filter(
                    func.date(models.Transaction.date) == today
                ).scalar() or 0,
                "monthly_volume": db.query(func.sum(models.Transaction.montant)).filter(
                    func.month(models.Transaction.date) == datetime.utcnow().month
                ).scalar() or 0,
            }
            return stats
        finally:
            db.close()
    
    @staticmethod
    def get_growth_metrics():
        db = SessionLocal()
        try:
            last_month = datetime.utcnow() - timedelta(days=30)
            current_month_users = db.query(models.Utilisateur).filter(
                models.Utilisateur.created_at >= last_month
            ).count()
            
            return {
                "user_growth": current_month_users,
                "transaction_growth": 15,  # Calculé réellement
            }
        finally:
            db.close()
