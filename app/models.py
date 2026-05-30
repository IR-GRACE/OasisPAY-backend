from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN_ECOLE = "admin_ecole"
    DIRECTEUR = "directeur"
    COMPTABLE = "comptable"
    CAISSIER = "caissier"
    ENSEIGNANT = "enseignant"
    PARENT = "parent"

class StatutPaiementEnum(str, enum.Enum):
    PAYE = "paye"
    EN_ATTENTE = "en_attente"
    ANNULE = "annule"

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String)
    email = Column(String, unique=True, index=True, nullable=False)
    telephone = Column(String)
    hashed_password = Column(String, nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.PARENT)
    actif = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Etudiant(Base):
    __tablename__ = "etudiants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    matricule = Column(String, unique=True, index=True, nullable=False)
    ecole_id = Column(Integer)
    classe_id = Column(Integer)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, nullable=False)
    montant = Column(Float, nullable=False)
    devise = Column(String, default="CDF")
    type_frais = Column(String, nullable=False)
    statut = Column(SQLEnum(StatutPaiementEnum), default=StatutPaiementEnum.PAYE)
    methode_paiement = Column(String)
    reference = Column(String, unique=True, index=True)
    numero_transaction = Column(String)
    date = Column(DateTime, default=datetime.utcnow)
    caissier_id = Column(Integer)
    notes = Column(Text)
    recu_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
