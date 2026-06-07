from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Numeric, JSON, UUID, BigInteger
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import INET
from app.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    telephone = Column(String(20), unique=True)
    hashed_password = Column(String(60), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    actif = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    refresh_token = Column(Text, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(INET)
    device_fingerprint = Column(Text)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OtpCode(Base):
    __tablename__ = "otp_codes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    code = Column(String(255), nullable=False)
    type = Column(String(20), nullable=False)
    purpose = Column(String(50), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    ip_address = Column(INET)
    user_agent = Column(Text)
    old_value = Column(JSON)
    new_value = Column(JSON)
    status = Column(String(20))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Etudiant(Base):
    __tablename__ = "etudiants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    prenom = Column(String(100))
    matricule = Column(String(50), unique=True)
    parent_id = Column(Integer, ForeignKey("users.id"))
    classe_id = Column(Integer, ForeignKey("classes.id"))
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Classe(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100))
    niveau = Column(String(50))
    frais_inscription = Column(Numeric(10,2), default=0)
    frais_mensuel = Column(Numeric(10,2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Paiement(Base):
    __tablename__ = "paiements"
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(100), unique=True)
    etudiant_id = Column(Integer, ForeignKey("etudiants.id"))
    montant = Column(Numeric(10,2))
    devise = Column(String(3), default="CDF")
    type_frais = Column(String(50))
    methode_paiement = Column(String(50))
    numero_telephone = Column(String(20))
    statut = Column(String(20), default="pending")
    transaction_id = Column(String(100))
    date_paiement = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Autres modèles (Transaction, Wallet, etc.) peuvent être ajoutés ici si nécessaire