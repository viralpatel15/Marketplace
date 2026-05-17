from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.product import Product
from app.models.company import Company
from app.models.category import Category

router = APIRouter()


@router.get("/sitemap/products")
async def sitemap_products(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product.slug, Product.updated_at).where(Product.status == "active"))
    return {"data": [{"slug": r.slug, "updated_at": r.updated_at.isoformat()} for r in result]}


@router.get("/sitemap/companies")
async def sitemap_companies(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company.slug, Company.updated_at).where(Company.is_active == True))
    return {"data": [{"slug": r.slug, "updated_at": r.updated_at.isoformat()} for r in result]}


@router.get("/sitemap/categories")
async def sitemap_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category.slug).where(Category.is_active == True))
    return {"data": [{"slug": r.slug} for r in result]}
