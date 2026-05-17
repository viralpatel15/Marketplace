from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id           = Column(Integer, primary_key=True, autoincrement=True)
    name         = Column(String(100), nullable=False)
    email        = Column(String(255), unique=True, nullable=False, index=True)
    phone        = Column(String(15), unique=True, nullable=True, index=True)
    password_hash= Column(String(255), nullable=True)
    role         = Column(String(20), nullable=False, default="buyer")
    is_verified  = Column(Boolean, default=False, nullable=False)
    google_id    = Column(String(100), nullable=True)
    avatar_url   = Column(String(500), nullable=True)
    is_active    = Column(Boolean, default=True, nullable=False)
    last_login   = Column(DateTime, nullable=True)
    created_at   = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at   = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company   = relationship("Company", back_populates="owner", uselist=False)
    inquiries = relationship("Inquiry", back_populates="buyer")
