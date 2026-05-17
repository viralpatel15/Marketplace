from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, DECIMAL, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    company_id    = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    category_id   = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    name          = Column(String(300), nullable=False)
    slug          = Column(String(300), unique=True, nullable=False, index=True)
    description   = Column(Text, nullable=False)
    price_min     = Column(DECIMAL(12, 2), nullable=True)
    price_max     = Column(DECIMAL(12, 2), nullable=True)
    unit          = Column(String(50), nullable=False, default="piece")
    moq           = Column(Integer, nullable=False, default=1)
    images        = Column(ARRAY(Text), nullable=False, default=[])
    tags          = Column(ARRAY(Text), nullable=True)
    specifications= Column(JSONB, nullable=True)
    is_featured   = Column(Boolean, default=False, nullable=False, index=True)
    status        = Column(String(20), default="active", nullable=False, index=True)
    views         = Column(Integer, default=0, nullable=False)
    inquiry_count = Column(Integer, default=0, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at    = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company   = relationship("Company", back_populates="products")
    category  = relationship("Category", back_populates="products")
    inquiries = relationship("Inquiry", back_populates="product")
    leads     = relationship("Lead", back_populates="product")
