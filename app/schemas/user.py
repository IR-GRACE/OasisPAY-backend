from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    email: str
    full_name: Optional[str] = Field(None, description="Nom complet de l'User")


class UserRegisterRequest(BaseModel):
    email: str = Field(..., description="Email de l'User")
    password: str = Field(..., min_length=6, description="Mot de passe")
    full_name: str = Field(..., description="Nom complet de l'User")
    role: str = Field(..., description="Rôle de l'User")
    student_id: Optional[str] = Field(None, description="Matricule de l'étudiant")


class UserRead(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    role: str
    student_id: Optional[str]
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class UserStatusUpdate(BaseModel):
    approved: bool = Field(True, description="Approuver ou rejeter l'User")


class UserUpdate(BaseModel):
    email: Optional[str]
    full_name: Optional[str]
    status: Optional[str]
    is_active: Optional[bool]
