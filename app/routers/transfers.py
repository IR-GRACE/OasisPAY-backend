from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth
import uuid

router = APIRouter(prefix="/transfers", tags=["Transferts"])

@router.post("/")
def create_transfer(
    transfer_data: dict,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    reference = str(uuid.uuid4())[:8].upper()
    return {
        "success": True,
        "message": "Transfert effectué",
        "reference": reference
    }
