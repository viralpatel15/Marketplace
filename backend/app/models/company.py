from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id               = Column(Integer, primary_key=True, autoincrement=True)
    user_id          = Column(Integer, ForeignKey("users.id"), nullable=False)
    plan_id          = Column(Integer, ForeignKey("plans.id"), nullable=True)
    name             = Column(String(200), nullable=False)
    slug             = Column(String(200), unique=True, nullable=False, index=True)
    gst_number       = Column(String(20), nullable=True)
    description      = Column(Text, nullable=True)
    address          = Column(Text, nullable=True)
    city             = Column(String(100), nullable=False, index=True)
    state            = Column(String(100), nullable=False)
    pincode          = Column(String(10), nullable=True)
    category         = Column(String(100), nullable=False, index=True)
    logo_url         = Column(String(500), nullable=True)
    phone            = Column(String(15), nullable=False)
    website          = Column(String(300), nullable=True)
    year_established = Column(Integer, nullable=True)
    employee_count   = Column(String(50), nullable=True)
    is_verified      = Column(Boolean, default=False, nullable=False, index=True)
    is_active        = Column(Boolean, default=True, nullable=False)
    total_leads      = Column(Integer, default=0, nullable=False)
    created_at       = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at       = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    owner        = relationship("User", back_populates="company")
    plan         = relationship("Plan", foreign_keys=[plan_id])
    products     = relationship("Product", back_populates="company", cascade="all, delete-orphan")
    subscription = relationship("Subscription", back_populates="company", uselist=False)
    leads        = relationship("Lead", back_populates="company")
