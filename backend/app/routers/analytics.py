from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import require_seller
from app.models.user import User
from app.models.company import Company
from app.models.plan import Plan
from app.models.product import Product
from app.models.lead import Lead
from app.models.inquiry import Inquiry

router = APIRouter()


async def get_seller_company_with_plan(user: User, db: AsyncSession) -> tuple:
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company found")

    plan = None
    if company.plan_id:
        plan_result = await db.execute(select(Plan).where(Plan.id == company.plan_id))
        plan = plan_result.scalar_one_or_none()

    if not plan or not plan.has_analytics:
        raise HTTPException(status_code=403, detail="Analytics require Basic plan or above")

    return company, plan


@router.get("/overview")
async def analytics_overview(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company, plan = await get_seller_company_with_plan(user, db)
    since = datetime.utcnow() - timedelta(days=30)

    total_views = (await db.execute(
        select(func.sum(Product.views)).where(Product.company_id == company.id)
    )).scalar() or 0

    total_leads = (await db.execute(
        select(func.count(Lead.id)).where(Lead.company_id == company.id, Lead.created_at >= since)
    )).scalar() or 0

    total_inquiries = (await db.execute(
        select(func.count(Inquiry.id)).where(Inquiry.company_id == company.id, Inquiry.created_at >= since)
    )).scalar() or 0

    conversion_rate = round((total_inquiries / total_views * 100) if total_views > 0 else 0, 2)

    return {"data": {
        "period": f"{since.date()} to {datetime.utcnow().date()}",
        "total_views": total_views,
        "total_leads": total_leads,
        "total_inquiries": total_inquiries,
        "conversion_rate": conversion_rate,
    }}


@router.get("/products")
async def analytics_products(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company, plan = await get_seller_company_with_plan(user, db)
    products = (await db.execute(
        select(Product).where(Product.company_id == company.id, Product.status != "deleted")
    )).scalars().all()
    return {"data": [{"id": p.id, "name": p.name, "views": p.views, "inquiry_count": p.inquiry_count} for p in products]}


@router.get("/leads-trend")
async def leads_trend(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company, plan = await get_seller_company_with_plan(user, db)
    since = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.date(Lead.created_at).label("date"), func.count(Lead.id).label("count"))
        .where(Lead.company_id == company.id, Lead.created_at >= since)
        .group_by(func.date(Lead.created_at))
        .order_by(func.date(Lead.created_at))
    )
    return {"data": [{"date": str(row.date), "count": row.count} for row in result]}


@router.get("/top-products")
async def top_products(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company, plan = await get_seller_company_with_plan(user, db)
    by_views = (await db.execute(
        select(Product).where(Product.company_id == company.id, Product.status != "deleted")
        .order_by(Product.views.desc()).limit(5)
    )).scalars().all()
    by_leads = (await db.execute(
        select(Product).where(Product.company_id == company.id, Product.status != "deleted")
        .order_by(Product.inquiry_count.desc()).limit(5)
    )).scalars().all()
    return {"data": {
        "by_views": [{"id": p.id, "name": p.name, "views": p.views} for p in by_views],
        "by_leads": [{"id": p.id, "name": p.name, "leads": p.inquiry_count} for p in by_leads],
    }}


@router.get("/buyer-cities")
async def buyer_cities(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company, plan = await get_seller_company_with_plan(user, db)
    result = await db.execute(
        select(Lead.buyer_city, func.count(Lead.id).label("count"))
        .where(Lead.company_id == company.id, Lead.buyer_city != None)
        .group_by(Lead.buyer_city)
        .order_by(func.count(Lead.id).desc())
        .limit(10)
    )
    return {"data": [{"city": row.buyer_city, "count": row.count} for row in result]}
