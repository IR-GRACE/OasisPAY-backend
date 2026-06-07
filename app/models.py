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
    code = Column(String(255), nullable=False)  # token ou code
    type = Column(String(20), nullable=False)  # email, sms
    purpose = Column(String(50), nullable=False)  # email_verification, password_reset, login
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

# Autres modèles existants (Etudiant, Classe, Paiement, etc.) à conserver
# Si vous avez déjà ces classes, assurez-vous qu'elles ne sont pas dupliquées