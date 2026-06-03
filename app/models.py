from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Admin(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100))
    telephone = Column(String(20), unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="admin")
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
    role = Column(String(50), default="parent")
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

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

class Paiement(Base):
    __tablename__ = "paiements"

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, nullable=False)
    montant = Column(Float, nullable=False)
    devise = Column(String(3), default='CDF')
    type_frais = Column(String(100))
    methode_paiement = Column(String(50))
    numero_telephone = Column(String(32))
    statut = Column(String(50), default="en_attente")
    reference = Column(String(100), unique=True, index=True)
    transaction_id = Column(String(255))
    date_paiement = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class Classe(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, nullable=False)
    frais_scolarite = Column(Float, default=0)
