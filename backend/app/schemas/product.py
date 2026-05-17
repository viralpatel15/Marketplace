from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from decimal import Decimal


class ProductCreate(BaseModel):
    name: str
    category_id: int
    description: str
    unit: str = "piece"
    moq: int = 1
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    tags: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    description: Optional[str] = None
    unit: Optional[str] = None
    moq: Optional[int] = None
    price_min: Optional[Decimal] = None
    price_max: Optional[Decimal] = None
    tags: Optional[List[str]] = None
    specifications: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProductResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str
    unit: str
    moq: int
    price_min: Optional[Decimal]
    price_max: Optional[Decimal]
    images: List[str]
    tags: Optional[List[str]]
    specifications: Optional[Dict[str, Any]]
    is_featured: bool
    status: str
    views: int
    inquiry_count: int
    company_id: int
    category_id: int

    class Config:
        from_attributes = True
