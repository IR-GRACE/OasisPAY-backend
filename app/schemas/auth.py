from typing import Optional

from pydantic import BaseModel, Field


class AuthLoginRequest(BaseModel):
    email: str = Field(..., description="Email de l'User")
    password: str = Field(..., description="Mot de passe")


class AuthRegisterRequest(BaseModel):
    email: str = Field(..., description="Email de l'User")
    password: str = Field(..., min_length=6, description="Mot de passe")
    full_name: str = Field(..., description="Nom complet de l'User")
    role: str = Field(..., description="Rôle de l'User")
    student_id: Optional[str] = Field(None, description="Matricule de l'étudiant")


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = Field("bearer")
    user: dict
