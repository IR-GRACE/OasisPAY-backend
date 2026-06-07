from sqlalchemy.orm import Session
from ..models import AuditLog

def log_audit(db: Session, user_id: int, action: str, resource_type: str = None,
              resource_id: str = None, ip: str = None, ua: str = None,
              old: dict = None, new: dict = None, status: str = "success"):
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip,
        user_agent=ua,
        old_value=old,
        new_value=new,
        status=status
    )
    db.add(log)
    db.commit()