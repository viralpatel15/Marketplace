import re
import io
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_seller
from app.models.product import Product
from app.models.company import Company
from app.models.plan import Plan
from app.models.user import User
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.services.storage_service import upload_file, delete_file
from app.services.search_service import index_product, delete_product, search_products
import redis.asyncio as aioredis
from app.core.config import settings

router = APIRouter()


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_-]+", "-", text)


async def make_unique_product_slug(base: str, db: AsyncSession) -> str:
    slug = slugify(base)
    candidate = slug
    i = 1
    while True:
        result = await db.execute(select(Product).where(Product.slug == candidate))
        if not result.scalar_one_or_none():
            return candidate
        candidate = f"{slug}-{i}"
        i += 1


async def get_seller_company(user: User, db: AsyncSession) -> Company:
    result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=400, detail="Create a company profile first")
    return company


async def check_product_limit(company: Company, db: AsyncSession):
    if not company.plan_id:
        plan_result = await db.execute(select(Plan).where(Plan.name == "Free"))
        plan = plan_result.scalar_one_or_none()
    else:
        plan_result = await db.execute(select(Plan).where(Plan.id == company.plan_id))
        plan = plan_result.scalar_one_or_none()

    if plan and plan.max_products != -1:
        count_result = await db.execute(
            select(func.count()).where(Product.company_id == company.id, Product.status != "deleted")
        )
        count = count_result.scalar()
        if count >= plan.max_products:
            raise HTTPException(status_code=403, detail=f"Product limit reached for your plan ({plan.max_products} max). Upgrade to add more.")


@router.post("", status_code=201)
async def create_product(data: ProductCreate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company = await get_seller_company(user, db)
    await check_product_limit(company, db)

    slug = await make_unique_product_slug(f"{data.name} {company.slug}", db)
    product = Product(**data.model_dump(), company_id=company.id, slug=slug, images=[])
    db.add(product)
    await db.commit()
    await db.refresh(product)

    index_product({**product.__dict__, "city": company.city, "company_name": company.name})
    return {"data": ProductResponse.model_validate(product)}


@router.get("/search")
async def search(
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    is_verified: Optional[bool] = Query(None),
    sort: str = Query("views"),
    order: str = Query("desc"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    filters = {k: v for k, v in {"category_id": category_id, "city": city, "price_min": price_min,
                                   "price_max": price_max}.items() if v is not None}
    results = search_products(q or "", filters, sort, order, page, limit)
    return {"data": results.get("hits", []), "meta": {"total": results.get("estimatedTotalHits", 0)}}


@router.get("/featured")
async def featured_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.is_featured == True, Product.status == "active").limit(8))
    products = result.scalars().all()
    return {"data": [ProductResponse.model_validate(p) for p in products]}


@router.get("/my")
async def my_products(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db), page: int = Query(1, ge=1), limit: int = Query(20)):
    company = await get_seller_company(user, db)
    query = select(Product).where(Product.company_id == company.id, Product.status != "deleted")
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    products = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [ProductResponse.model_validate(p) for p in products], "meta": {"page": page, "limit": limit, "total": total}}


@router.get("/{slug}")
async def get_product(slug: str, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.slug == slug, Product.status == "active"))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    async def increment_view(product_id: int):
        r = aioredis.from_url(settings.REDIS_URL)
        await r.incr(f"product_views:{product_id}")
        await r.aclose()

    background_tasks.add_task(increment_view, product.id)
    return {"data": ProductResponse.model_validate(product)}


@router.get("")
async def list_products(
    category_id: Optional[int] = Query(None),
    city: Optional[str] = Query(None),
    price_min: Optional[float] = Query(None),
    price_max: Optional[float] = Query(None),
    is_featured: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Product).where(Product.status == "active")
    if category_id:
        query = query.where(Product.category_id == category_id)
    if is_featured is not None:
        query = query.where(Product.is_featured == is_featured)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    products = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    return {"data": [ProductResponse.model_validate(p) for p in products], "meta": {"page": page, "limit": limit, "total": total}}


@router.put("/{product_id}")
async def update_product(product_id: int, data: ProductUpdate, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company = await get_seller_company(user, db)
    result = await db.execute(select(Product).where(Product.id == product_id, Product.company_id == company.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    index_product({**product.__dict__, "city": company.city, "company_name": company.name})
    return {"data": ProductResponse.model_validate(product)}


@router.delete("/{product_id}")
async def delete_product_endpoint(product_id: int, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company = await get_seller_company(user, db)
    result = await db.execute(select(Product).where(Product.id == product_id, Product.company_id == company.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = "deleted"
    await db.commit()
    delete_product(product_id)
    return {"data": {"message": "Product deleted"}}


@router.post("/{product_id}/images")
async def upload_images(
    product_id: int,
    files: List[UploadFile] = File(...),
    user: User = Depends(require_seller),
    db: AsyncSession = Depends(get_db),
):
    company = await get_seller_company(user, db)
    result = await db.execute(select(Product).where(Product.id == product_id, Product.company_id == company.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if len(product.images or []) + len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 images per product")

    urls = list(product.images or [])
    for f in files:
        content = await f.read()
        url = await upload_file(content, f.filename or "image.jpg", f"products/{product_id}")
        urls.append(url)

    product.images = urls
    await db.commit()
    return {"data": {"images": urls}}


@router.delete("/{product_id}/images/{idx}")
async def delete_image(product_id: int, idx: int, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company = await get_seller_company(user, db)
    result = await db.execute(select(Product).where(Product.id == product_id, Product.company_id == company.id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    images = list(product.images or [])
    if idx < 0 or idx >= len(images):
        raise HTTPException(status_code=400, detail="Invalid image index")
    removed = images.pop(idx)
    product.images = images
    await db.commit()
    await delete_file(removed)
    return {"data": {"images": images}}
