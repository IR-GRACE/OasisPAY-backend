from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# ==================== AUTH ====================
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict

# ==================== PAIEMENTS ====================
class PaiementCreate(BaseModel):
    etudiant_id: int
    montant: float
    type_frais: str
    methode_paiement: str
    numero_telephone: str
    devise: str = 'CDF'
class PaiementResponse(BaseModel):
    id: int
    reference: str
    etudiant_id: int
    montant: float
    type_frais: str
    methode_paiement: str
    statut: str
    transaction_id: Optional[str] = None
    numero_telephone: Optional[str] = None
    date_paiement: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ==================== ETUDIANTS ====================
class EtudiantCreate(BaseModel):
    nom: str
    prenom: str
    matricule: Optional[str] = None
    classe_id: int
    parent_id: Optional[int] = None

class EtudiantResponse(EtudiantCreate):
    id: int
    actif: bool
    created_at: datetime

# ==================== CLASSES ====================
class ClasseCreate(BaseModel):
    nom: str
    niveau: str
    frais_inscription: Optional[float] = 0
    frais_mensuel: Optional[float] = 0

class ClasseResponse(ClasseCreate):
    id: int
    created_at: datetime

# ==================== UTILISATEURS ====================
class UtilisateurCreate(BaseModel):
    email: str
    password: str
    nom: str
    prenom: str
    telephone: str
    role: str = "parent"

class UtilisateurResponse(BaseModel):
    id: int
    email: str
    nom: str
    prenom: str
    telephone: Optional[str] = None
    role: str
    actif: bool
    created_at: datetime

# ==================== AUTRES ====================
class DashboardStats(BaseModel):
    total_etudiants: int
    total_enseignants: int
    total_paiements: float
    paiements_ce_mois: float



