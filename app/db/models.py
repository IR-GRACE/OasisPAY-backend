from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func

from app.db.base import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    etudiant_id = Column(Integer, nullable=False, index=True)
    montant = Column(Float, nullable=False)
    devise = Column(String(10), nullable=False, default="CDF")
    type_frais = Column(String(100), nullable=True)
    methode_paiement = Column(String(50), nullable=False)
    provider = Column(String(50), nullable=False)
    numero_telephone = Column(String(32), nullable=True)
    transaction_ref = Column(String(64), nullable=False, unique=True, index=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    provider_reference = Column(String(128), nullable=True)
    raw_payload = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(256), nullable=False, unique=True, index=True)
    full_name = Column(String(128), nullable=True)
    password_hash = Column(String(256), nullable=True)
    role = Column(String(64), nullable=False, default="parent", index=True)
    student_id = Column(String(64), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="pending", index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=False, unique=True, index=True)
    code_hash = Column(String(256), nullable=False)
    api_key = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    actor = Column(String(128), nullable=False)
    action = Column(String(128), nullable=False)
    target_type = Column(String(64), nullable=True)
    target_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
