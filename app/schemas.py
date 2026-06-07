from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class RoleEnum(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN_ECOLE = "admin_ecole"
    DIRECTEUR = "directeur"
    COMPTABLE = "comptable"
    CAISSIER = "caissier"
    ENSEIGNANT = "enseignant"
    PARENT = "parent"
    ELEVE = "eleve"

class StatutPaiementEnum(str, Enum):
    PAYE = "paye"
    PARTIEL = "partiel"
    EN_ATTENTE = "en_attente"
    ANNULE = "annule"

class TypeFraisEnum(str, Enum):
    INSCRIPTION = "inscription"
    SCOLARITE = "scolarite"
    EXAMEN = "examen"
    CANTINE = "cantine"
    TRANSPORT = "transport"
    UNIFORME = "uniforme"
    ACTIVITE = "activite"
    AUTRE = "autre"

# Auth
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: "UtilisateurResponse"

# Utilisateurs
class UtilisateurCreate(BaseModel):
    nom: str
    prenom: Optional[str] = None
    email: EmailStr
    telephone: Optional[str] = None
    password: str
    role: RoleEnum = RoleEnum.PARENT
    ecole_id: Optional[int] = None

class UtilisateurUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    photo_url: Optional[str] = None
    actif: Optional[bool] = None

class UtilisateurResponse(BaseModel):
    id: int
    nom: str
    prenom: Optional[str] = None
    email: str
    telephone: Optional[str] = None
    photo_url: Optional[str] = None
    role: RoleEnum
    ecole_id: Optional[int] = None
    actif: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Élèves
class EtudiantCreate(BaseModel):
    nom: str
    prenom: str
    matricule: str
    date_naissance: Optional[datetime] = None
    sexe: Optional[str] = None
    ecole_id: int
    classe_id: Optional[int] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    boursier: bool = False
    pourcentage_bourse: float = 0.0

class EtudiantResponse(EtudiantCreate):
    id: int
    actif: bool
    created_at: datetime
    classe_nom: Optional[str] = None
    parent_nom: Optional[str] = None
    
    class Config:
        from_attributes = True

# Classes
class ClasseCreate(BaseModel):
    nom: str
    niveau: Optional[str] = None
    ecole_id: int
    annee_scolaire: str
    capacite: int = 50
    titulaire_id: Optional[int] = None

class ClasseResponse(ClasseCreate):
    id: int
    created_at: datetime
    titulaire_nom: Optional[str] = None
    
    class Config:
        from_attributes = True

# Frais
class FraisCreate(BaseModel):
    ecole_id: int
    nom: str
    type: TypeFraisEnum = TypeFraisEnum.SCOLARITE
    montant: float
    devise: str = "CDF"
    annee_scolaire: str
    obligatoire: bool = True
    par_trimestre: bool = False
    description: Optional[str] = None

class FraisResponse(FraisCreate):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Paiements
class PaiementCreate(BaseModel):
    etudiant_id: int
    frais_id: Optional[int] = None
    montant: float
    devise: str = "CDF"
    type_frais: str
    methode_paiement: str
    notes: Optional[str] = None

class PaiementResponse(BaseModel):
    id: int
    etudiant_id: int
    etudiant_nom: str
    montant: float
    devise: str
    type_frais: str
    statut: StatutPaiementEnum
    methode_paiement: str
    reference: str
    date: datetime
    caissier_nom: Optional[str] = None
    recu_url: Optional[str] = None
    
    class Config:
        from_attributes = True

# Examens
class ExamenCreate(BaseModel):
    classe_id: int
    matiere: str
    date: datetime
    coefficient: float = 1.0
    trimestre: int = 1

class ExamenResponse(ExamenCreate):
    id: int
    created_at: datetime
    classe_nom: Optional[str] = None
    
    class Config:
        from_attributes = True

class NoteCreate(BaseModel):
    etudiant_id: int
    examen_id: int
    valeur: float
    appreciation: Optional[str] = None

class NoteResponse(NoteCreate):
    id: int
    etudiant_nom: str
    examen_matiere: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Présences
class PresenceCreate(BaseModel):
    etudiant_id: int
    present: bool = True
    justifie: bool = False
    motif: Optional[str] = None

class PresenceResponse(PresenceCreate):
    id: int
    date: datetime
    
    class Config:
        from_attributes = True

# Emploi du temps
class EmploiDuTempsCreate(BaseModel):
    classe_id: int
    jour: str
    heure_debut: str
    heure_fin: str
    matiere: str
    enseignant: Optional[str] = None
    salle: Optional[str] = None

class EmploiDuTempsResponse(EmploiDuTempsCreate):
    id: int
    created_at: datetime
    classe_nom: Optional[str] = None
    
    class Config:
        from_attributes = True

# Notifications
class NotificationCreate(BaseModel):
    utilisateur_id: Optional[int] = None
    ecole_id: Optional[int] = None
    titre: str
    message: str
    type: str = "email"
    destinataire: str

class NotificationResponse(NotificationCreate):
    id: int
    lue: bool
    date_envoi: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Statistiques
class DashboardStats(BaseModel):
    total_etudiants: int
    total_paiements: int
    total_encaisse: float
    taux_paiement: float
    paiements_en_attente: int
    total_classes: int
    total_utilisateurs: int
    total_presences_mois: int

class PaiementStats(BaseModel):
    total_journalier: float
    total_mensuel: float
    total_annuel: float
    par_methode: dict
    evolution_mensuelle: List[dict]

class PresenceStats(BaseModel):
    total_presences: int
    total_absences: int
    taux_presence: float
    par_classe: List[dict]

class NotesStats(BaseModel):
    moyenne_generale: float
    meilleure_note: float
    plus_faible_note: float
    par_matiere: List[dict]
