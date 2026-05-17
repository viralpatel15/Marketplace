from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    company_id  = Column(Integer, ForeignKey("companies.id"), nullable=False)
    inquiry_id  = Column(Integer, ForeignKey("inquiries.id"), nullable=True)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=True)
    buyer_name  = Column(String(100), nullable=False)
    buyer_phone = Column(String(15), nullable=False)
    buyer_email = Column(String(255), nullable=False)
    buyer_city  = Column(String(100), nullable=True)
    quantity    = Column(Integer, nullable=True)
    source      = Column(String(50), nullable=False, default="inquiry")
    is_viewed   = Column(Boolean, default=False, nullable=False)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="leads")
    inquiry = relationship("Inquiry", back_populates="lead")
    product = relationship("Product", back_populates="leads")
