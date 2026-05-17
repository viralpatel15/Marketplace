from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.core.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"

    id                      = Column(Integer, primary_key=True, autoincrement=True)
    company_id              = Column(Integer, ForeignKey("companies.id"), unique=True, nullable=False)
    plan_id                 = Column(Integer, ForeignKey("plans.id"), nullable=False)
    razorpay_sub_id         = Column(String(100), nullable=True)
    razorpay_customer_id    = Column(String(100), nullable=True)
    status                  = Column(String(30), nullable=False, default="trial")
    start_date              = Column(Date, nullable=False)
    end_date                = Column(Date, nullable=True)
    trial_end               = Column(Date, nullable=True)
    cancel_at_period_end    = Column(Boolean, default=False, nullable=False)
    last_payment_at         = Column(DateTime, nullable=True)
    next_billing_at         = Column(DateTime, nullable=True)
    amount_paid             = Column(DECIMAL(10, 2), nullable=True)
    created_at              = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at              = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    company = relationship("Company", back_populates="subscription")
    plan    = relationship("Plan")
