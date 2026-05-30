from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    phone: str = Field(..., description="Numéro de téléphone de l'admin")
    code: str = Field(..., description="Code secret de l'admin")


class AdminLoginResponse(BaseModel):
    name: str
    phone: str
    api_key: str


class AdminUserCreate(BaseModel):
    name: str = Field(..., description="Nom de l'administrateur")
    phone: str = Field(..., description="Téléphone de l'administrateur")
    code: str = Field(..., description="Code secret de l'administrateur")
    is_active: bool = Field(True, description="Activer ou désactiver l'administrateur")


class AdminUserUpdate(BaseModel):
    name: Optional[str] = Field(None, description="Nom de l'administrateur")
    code: Optional[str] = Field(None, description="Code secret de l'administrateur")
    is_active: Optional[bool] = Field(None, description="Activer ou désactiver l'administrateur")


class AdminUserRead(BaseModel):
    id: int
    name: str
    phone: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
