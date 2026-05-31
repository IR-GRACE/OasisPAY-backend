from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RoleEnum(str, enum.Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    DIRECTEUR = "directeur"
    PARENT = "parent"
    ELEVE = "eleve"

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    telephone = Column(String(20), unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.ADMIN)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    telephone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(RoleEnum), default=RoleEnum.PARENT)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Etudiant(Base):
    __tablename__ = "etudiants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    prenom = Column(String, nullable=False)
    matricule = Column(String, unique=True, index=True, nullable=False)
    parent_id = Column(Integer, ForeignKey("utilisateurs.id"))
    classe_id = Column(Integer)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, nullable=False)
    montant = Column(Float, nullable=False)
    statut = Column(String, default="en_attente")
    reference = Column(String, unique=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
