from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.user import User
from app.models.company import Company
from app.models.product import Product
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.category import Category
from app.schemas.company import CompanyResponse
from app.schemas.product import ProductResponse
from pydantic import BaseModel

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: Optional[int] = None
    description: Optional[str] = None
    sort_order: int = 0


class RejectRequest(BaseModel):
    reason: str


@router.get("/stats")
async def admin_stats(user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    today = datetime.utcnow().date()
    total_companies = (await db.execute(select(func.count(Company.id)).where(Company.is_active == True))).scalar()
    total_products = (await db.execute(select(func.count(Product.id)).where(Product.status == "active"))).scalar()
    active_subs = (await db.execute(select(func.count(Subscription.id)).where(Subscription.status == "active"))).scalar()
    new_today = (await db.execute(select(func.count(Company.id)).where(func.date(Company.created_at) == today))).scalar()

    mrr_result = await db.execute(
        select(func.sum(Plan.price_monthly))
        .join(Subscription, Subscription.plan_id == Plan.id)
        .where(Subscription.status == "active")
    )
    mrr = float(mrr_result.scalar() or 0)

    return {"data": {
        "total_companies": total_companies,
        "total_products": total_products,
        "active_subscriptions": active_subs,
        "new_signups_today": new_today,
        "mrr": mrr,
    }}


@router.get("/companies")
async def list_all_companies(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    is_verified: Optional[bool] = Query(None),
    city: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20),
):
    query = select(Company).where(Company.is_active == True)
    if is_verified is not None:
        query = query.where(Company.is_verified == is_verified)
    if city:
        query = query.where(Company.city.ilike(f"%{city}%"))
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    companies = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [CompanyResponse.model_validate(c) for c in companies], "meta": {"total": total}}


@router.get("/companies/pending")
async def pending_companies(user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.is_verified == False, Company.gst_number != None, Company.is_active == True))
    companies = result.scalars().all()
    return {"data": [CompanyResponse.model_validate(c) for c in companies]}


@router.put("/companies/{company_id}/verify")
async def verify_company(company_id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company.is_verified = True
    await db.commit()
    return {"data": {"message": "Company verified"}}


@router.put("/companies/{company_id}/reject")
async def reject_company(company_id: int, data: RejectRequest, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return {"data": {"message": f"Company rejected: {data.reason}"}}


@router.delete("/companies/{company_id}")
async def delete_company(company_id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    company.is_active = False
    for product in company.products:
        product.status = "deleted"
    await db.commit()
    return {"data": {"message": "Company deleted"}}


@router.get("/products")
async def list_all_products(
    user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20),
):
    query = select(Product)
    if status:
        query = query.where(Product.status == status)
    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    products = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [ProductResponse.model_validate(p) for p in products], "meta": {"total": total}}


@router.put("/products/{product_id}/feature")
async def toggle_feature(product_id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_featured = not product.is_featured
    await db.commit()
    return {"data": {"is_featured": product.is_featured}}


@router.get("/users")
async def list_users(user: User = Depends(require_admin), db: AsyncSession = Depends(get_db),
                     role: Optional[str] = Query(None), page: int = Query(1, ge=1), limit: int = Query(20)):
    query = select(User)
    if role:
        query = query.where(User.role == role)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    users = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [{"id": u.id, "name": u.name, "email": u.email, "role": u.role, "is_active": u.is_active} for u in users], "meta": {"total": total}}


@router.put("/users/{user_id}/ban")
async def ban_user(user_id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = False
    await db.commit()
    return {"data": {"message": "User banned"}}


@router.post("/categories")
async def create_category(data: CategoryCreate, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Category).where(Category.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Slug already exists")
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return {"data": {"id": category.id, "name": category.name, "slug": category.slug}}


@router.put("/categories/{category_id}")
async def update_category(category_id: int, data: CategoryCreate, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(category, k, v)
    await db.commit()
    return {"data": {"message": "Category updated"}}


@router.delete("/categories/{category_id}")
async def delete_category(category_id: int, user: User = Depends(require_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category.is_active = False
    await db.commit()
    return {"data": {"message": "Category deleted"}}


@router.get("/subscriptions")
async def list_subscriptions(user: User = Depends(require_admin), db: AsyncSession = Depends(get_db),
                              status: Optional[str] = Query(None), page: int = Query(1, ge=1), limit: int = Query(20)):
    query = select(Subscription)
    if status:
        query = query.where(Subscription.status == status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    subs = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [{"id": s.id, "company_id": s.company_id, "plan_id": s.plan_id,
                      "status": s.status, "amount_paid": float(s.amount_paid or 0)} for s in subs], "meta": {"total": total}}
