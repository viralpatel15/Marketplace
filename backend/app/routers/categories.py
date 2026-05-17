from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.core.database import get_db
from app.models.category import Category

router = APIRouter()


@router.get("")
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.is_active == True).order_by(Category.sort_order))
    categories = result.scalars().all()
    return {"data": [{"id": c.id, "name": c.name, "slug": c.slug, "parent_id": c.parent_id,
                      "icon_url": c.icon_url, "product_count": c.product_count} for c in categories]}


@router.get("/{slug}")
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category).where(Category.slug == slug, Category.is_active == True))
    category = result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    children_result = await db.execute(select(Category).where(Category.parent_id == category.id, Category.is_active == True))
    children = children_result.scalars().all()
    return {"data": {"id": category.id, "name": category.name, "slug": category.slug,
                     "description": category.description, "icon_url": category.icon_url,
                     "children": [{"id": c.id, "name": c.name, "slug": c.slug} for c in children]}}


@router.get("/{slug}/products")
async def category_products(slug: str, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db)):
    from app.models.product import Product
    from sqlalchemy import func
    cat_result = await db.execute(select(Category).where(Category.slug == slug))
    category = cat_result.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    query = select(Product).where(Product.category_id == category.id, Product.status == "active")
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar()
    products = (await db.execute(query.offset((page - 1) * limit).limit(limit))).scalars().all()
    from app.schemas.product import ProductResponse
    return {"data": [ProductResponse.model_validate(p) for p in products], "meta": {"page": page, "limit": limit, "total": total}}
