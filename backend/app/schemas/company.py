from pydantic import BaseModel, HttpUrl
from typing import Optional


class CompanyCreate(BaseModel):
    name: str
    city: str
    state: str
    category: str
    phone: str
    description: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    website: Optional[str] = None
    year_established: Optional[int] = None
    employee_count: Optional[str] = None


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    category: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    pincode: Optional[str] = None
    gst_number: Optional[str] = None
    website: Optional[str] = None
    year_established: Optional[int] = None
    employee_count: Optional[str] = None


class CompanyResponse(BaseModel):
    id: int
    name: str
    slug: str
    city: str
    state: str
    category: str
    phone: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    is_verified: bool
    year_established: Optional[int]
    employee_count: Optional[str]
    total_leads: int
    website: Optional[str]

    class Config:
        from_attributes = True
