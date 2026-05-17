from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Inquiry(Base):
    __tablename__ = "inquiries"

    id          = Column(Integer, primary_key=True, autoincrement=True)
    buyer_id    = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=False)
    company_id  = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    quantity    = Column(Integer, nullable=True)
    message     = Column(Text, nullable=True)
    status      = Column(String(30), nullable=False, default="new", index=True)
    seller_note = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at  = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    buyer   = relationship("User", back_populates="inquiries")
    product = relationship("Product", back_populates="inquiries")
    company = relationship("Company")
    lead    = relationship("Lead", back_populates="inquiry", uselist=False)
