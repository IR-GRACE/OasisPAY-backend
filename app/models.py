from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    telephone = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    actif = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    etudiants = relationship("Etudiant", back_populates="parent")

class Etudiant(Base):
    __tablename__ = "etudiants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    matricule = Column(String(50), unique=True, index=True)
    parent_id = Column(Integer, ForeignKey("utilisateurs.id"))
    classe_id = Column(Integer)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    parent = relationship("Utilisateur", back_populates="etudiants")
    paiements = relationship("Paiement", back_populates="etudiant")

class Classe(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    frais_scolarite = Column(Float, default=0)

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"), nullable=False)
    montant = Column(Float, nullable=False)
    type_frais = Column(String(50), nullable=False)
    statut = Column(String(20), default="PENDING")
    methode_paiement = Column(String(50))
    reference = Column(String(100), unique=True, index=True)
    telephone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    etudiant = relationship("Etudiant", back_populates="paiements")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    type = Column(String(50), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Utilisateur", back_populates="notifications")