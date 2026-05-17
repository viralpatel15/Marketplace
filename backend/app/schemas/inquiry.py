from pydantic import BaseModel
from typing import Optional


class InquiryCreate(BaseModel):
    product_id: int
    quantity: Optional[int] = None
    message: Optional[str] = None


class InquiryStatusUpdate(BaseModel):
    status: str


class InquiryNoteUpdate(BaseModel):
    note: str


class InquiryResponse(BaseModel):
    id: int
    product_id: int
    company_id: int
    quantity: Optional[int]
    message: Optional[str]
    status: str

    class Config:
        from_attributes = True
