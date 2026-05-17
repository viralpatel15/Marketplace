"""Run once after migrations to seed plan data."""
import asyncio
from app.core.database import engine, SessionLocal
from app.models.plan import Plan


async def seed():
    async with SessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(Plan))
        if result.scalars().first():
            print("Plans already seeded.")
            return

        plans = [
            Plan(name="Free",       price_monthly=0,    max_products=5,   leads_per_month=3,  featured_listings=0, has_analytics=False, has_whatsapp=False, support_level="none"),
            Plan(name="Basic",      price_monthly=999,  max_products=50,  leads_per_month=20, featured_listings=0, has_analytics=True,  has_whatsapp=True,  support_level="email"),
            Plan(name="Pro",        price_monthly=2499, max_products=200, leads_per_month=-1, featured_listings=2, has_analytics=True,  has_whatsapp=True,  support_level="priority"),
            Plan(name="Enterprise", price_monthly=5999, max_products=-1,  leads_per_month=-1, featured_listings=5, has_analytics=True,  has_whatsapp=True,  support_level="dedicated"),
        ]
        db.add_all(plans)
        await db.commit()
        print("Plans seeded successfully.")


if __name__ == "__main__":
    asyncio.run(seed())
