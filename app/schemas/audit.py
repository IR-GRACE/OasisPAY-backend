from datetime import datetime
from pydantic import BaseModel


class AuditLogRead(BaseModel):
    id: int
    actor: str
    action: str
    target_type: str | None = None
    target_id: int | None = None
    details: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True
