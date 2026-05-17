import re
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_seller
from app.models.company import Company
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from app.services.storage_service import upload_file
from typing import Optional

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


async def make_unique_slug(base: str, db: AsyncSession) -> str:
    slug = slugify(base)
    candidate = slug
    i = 1
    while True:
        result = await db.execute(select(Company).where(Company.slug == candidate))
        if not result.scalar_one_or_none():
            return candidate
        candidate = f"{slug}-{i}"
        i += 1


@router.post("", status_code=201)
async def create_company(data: CompanyCreate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Company).where(Company.user_id == user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Company already exists for this seller")

    slug = await make_unique_slug(f"{data.name} {data.city}", db)
    company = Company(**data.model_dump(), user_id=user.id, slug=slug)
    db.add(company)
    await db.commit()
    await db.refresh(company)
    return {"data": CompanyResponse.model_validate(company)}


@router.get("/me")
async def get_my_company(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company profile found")
    return {"data": CompanyResponse.model_validate(company)}


@router.put("/me")
async def update_my_company(data: CompanyUpdate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company profile found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(company, k, v)
    await db.commit()
    await db.refresh(company)
    return {"data": CompanyResponse.model_validate(company)}


@router.post("/me/logo")
async def upload_logo(
    file: UploadFile = File(...),
    user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company profile found")
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    content = await file.read()
    url = await upload_file(content, file.filename or "logo.jpg", f"logos/{company.id}")
    company.logo_url = url
    await db.commit()
    return {"data": {"logo_url": url}}


@router.get("/{slug}")
async def get_company(slug: str, db: AsyncSession = Depends(get_db), current_user: Optional[User] = None):
    result = await db.execute(select(Company).where(Company.slug == slug, Company.is_active == True))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    data = CompanyResponse.model_validate(company)
    if not current_user:
        data.phone = None
    return {"data": data}


@router.get("")
async def list_companies(
    city: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_verified: Optional[bool] = Query(None),
    q: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    query = select(Company).where(Company.is_active == True)
    if city:
        query = query.where(Company.city.ilike(f"%{city}%"))
    if category:
        query = query.where(Company.category.ilike(f"%{category}%"))
    if is_verified is not None:
        query = query.where(Company.is_verified == is_verified)
    if q:
        query = query.where(Company.name.ilike(f"%{q}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()
    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    companies = result.scalars().all()
    return {"data": [CompanyResponse.model_validate(c) for c in companies],
            "meta": {"page": page, "limit": limit, "total": total}}
