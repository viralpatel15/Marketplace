from sqlalchemy import Column, Integer, String, Boolean, DECIMAL
from app.core.database import Base


class Plan(Base):
    __tablename__ = "plans"

    id                 = Column(Integer, primary_key=True, autoincrement=True)
    name               = Column(String(50), nullable=False)
    price_monthly      = Column(DECIMAL(10, 2), nullable=False)
    max_products       = Column(Integer, nullable=False)
    leads_per_month    = Column(Integer, nullable=False)
    featured_listings  = Column(Integer, default=0, nullable=False)
    has_analytics      = Column(Boolean, default=False, nullable=False)
    has_whatsapp       = Column(Boolean, default=False, nullable=False)
    support_level      = Column(String(50), nullable=False, default="none")
    razorpay_plan_id   = Column(String(100), nullable=True)
    is_active          = Column(Boolean, default=True, nullable=False)
