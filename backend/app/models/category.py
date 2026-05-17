from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id            = Column(Integer, primary_key=True, autoincrement=True)
    parent_id     = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name          = Column(String(100), nullable=False)
    slug          = Column(String(100), unique=True, nullable=False, index=True)
    description   = Column(Text, nullable=True)
    icon_url      = Column(String(500), nullable=True)
    sort_order    = Column(Integer, default=0, nullable=False)
    is_active     = Column(Boolean, default=True, nullable=False)
    product_count = Column(Integer, default=0, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow, nullable=False)

    children = relationship("Category", backref=__import__("sqlalchemy.orm", fromlist=["backref"]).backref("parent", remote_side="Category.id"))
    products = relationship("Product", back_populates="category")
