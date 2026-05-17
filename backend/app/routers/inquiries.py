from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_seller
from app.models.user import User
from app.models.inquiry import Inquiry
from app.models.lead import Lead
from app.models.product import Product
from app.models.company import Company
from app.schemas.inquiry import InquiryCreate, InquiryStatusUpdate, InquiryNoteUpdate, InquiryResponse
from app.services.whatsapp_service import send_lead_notification, send_inquiry_confirmation
from app.services.email_service import send_inquiry_confirmation_email

router = APIRouter()

VALID_STATUSES = ["new", "viewed", "contacted", "converted", "closed"]


def mask_contact(value: str) -> str:
    if not value:
        return "***"
    return value[:3] + "***" + value[-2:] if len(value) > 5 else "***"


@router.post("/inquiries", status_code=201)
async def submit_inquiry(data: InquiryCreate, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Phone verification required to send inquiries")

    product_result = await db.execute(select(Product).where(Product.id == data.product_id, Product.status == "active"))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    since = datetime.utcnow() - timedelta(hours=24)
    dup = await db.execute(select(Inquiry).where(
        Inquiry.buyer_id == user.id,
        Inquiry.product_id == data.product_id,
        Inquiry.created_at >= since
    ))
    if dup.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You already sent an inquiry for this product in the last 24 hours")

    company_result = await db.execute(select(Company).where(Company.id == product.company_id))
    company = company_result.scalar_one_or_none()

    inquiry = Inquiry(
        buyer_id=user.id,
        product_id=data.product_id,
        company_id=product.company_id,
        quantity=data.quantity,
        message=data.message,
    )
    db.add(inquiry)
    await db.flush()

    lead = Lead(
        company_id=product.company_id,
        inquiry_id=inquiry.id,
        product_id=data.product_id,
        buyer_name=user.name,
        buyer_phone=user.phone or "",
        buyer_email=user.email,
        quantity=data.quantity,
        source="inquiry",
    )
    db.add(lead)

    product.inquiry_count = (product.inquiry_count or 0) + 1
    company.total_leads = (company.total_leads or 0) + 1

    await db.commit()

    if company and company.phone:
        await send_lead_notification(company.phone, user.name, product.name, data.quantity or 1)
    if user.phone:
        await send_inquiry_confirmation(user.phone, product.name, company.name if company else "")
    await send_inquiry_confirmation_email(user.email, product.name, company.name if company else "")

    return {"data": InquiryResponse.model_validate(inquiry)}


@router.get("/inquiries/buyer")
async def buyer_inquiries(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(20)):
    from sqlalchemy import func
    query = select(Inquiry).where(Inquiry.buyer_id == user.id).order_by(Inquiry.created_at.desc())
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    inquiries = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [InquiryResponse.model_validate(i) for i in inquiries], "meta": {"total": total}}


@router.get("/inquiries/seller")
async def seller_inquiries(
    user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20),
):
    from sqlalchemy import func
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company found")

    query = select(Inquiry).where(Inquiry.company_id == company.id).order_by(Inquiry.created_at.desc())
    if status:
        query = query.where(Inquiry.status == status)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    inquiries = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [InquiryResponse.model_validate(i) for i in inquiries], "meta": {"total": total}}


@router.put("/inquiries/{inquiry_id}/status")
async def update_inquiry_status(inquiry_id: int, data: InquiryStatusUpdate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status. Valid: {VALID_STATUSES}")
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id, Inquiry.company_id == company.id))
    inquiry = result.scalar_one_or_none()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    inquiry.status = data.status
    await db.commit()
    return {"data": InquiryResponse.model_validate(inquiry)}


@router.post("/inquiries/{inquiry_id}/note")
async def add_inquiry_note(inquiry_id: int, data: InquiryNoteUpdate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    result = await db.execute(select(Inquiry).where(Inquiry.id == inquiry_id, Inquiry.company_id == company.id))
    inquiry = result.scalar_one_or_none()
    if not inquiry:
        raise HTTPException(status_code=404, detail="Inquiry not found")
    inquiry.seller_note = data.note
    await db.commit()
    return {"data": {"message": "Note saved"}}


@router.get("/leads")
async def get_leads(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db),
                    is_viewed: Optional[bool] = Query(None), page: int = Query(1, ge=1), limit: int = Query(20)):
    from sqlalchemy import func
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company found")

    query = select(Lead).where(Lead.company_id == company.id).order_by(Lead.created_at.desc())
    if is_viewed is not None:
        query = query.where(Lead.is_viewed == is_viewed)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    leads = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()

    lead_data = []
    for lead in leads:
        d = {
            "id": lead.id, "buyer_name": lead.buyer_name, "buyer_city": lead.buyer_city,
            "quantity": lead.quantity, "source": lead.source, "is_viewed": lead.is_viewed,
            "created_at": lead.created_at.isoformat(), "product_id": lead.product_id,
            "buyer_phone": lead.buyer_phone if company.plan_id else mask_contact(lead.buyer_phone),
            "buyer_email": lead.buyer_email if company.plan_id else mask_contact(lead.buyer_email),
        }
        lead_data.append(d)

    return {"data": lead_data, "meta": {"total": total}}


@router.put("/leads/{lead_id}/viewed")
async def mark_lead_viewed(lead_id: int, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    result = await db.execute(select(Lead).where(Lead.id == lead_id, Lead.company_id == company.id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    lead.is_viewed = True
    await db.commit()
    return {"data": {"message": "Lead marked as viewed"}}
