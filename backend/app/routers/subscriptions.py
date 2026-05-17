import json
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user, require_seller
from app.models.user import User
from app.models.company import Company
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.services.payment_service import (
    create_razorpay_customer, create_subscription, cancel_subscription, verify_webhook_signature
)
from app.services.whatsapp_service import send_subscription_receipt, send_payment_failed_alert
from app.core.config import settings
from pydantic import BaseModel

router = APIRouter()


class SubscribeRequest(BaseModel):
    plan_id: int


@router.get("/plans")
async def list_plans(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Plan).where(Plan.is_active == True))
    plans = result.scalars().all()
    return {"data": [{
        "id": p.id, "name": p.name, "price_monthly": float(p.price_monthly),
        "max_products": p.max_products, "leads_per_month": p.leads_per_month,
        "featured_listings": p.featured_listings, "has_analytics": p.has_analytics,
        "has_whatsapp": p.has_whatsapp, "support_level": p.support_level,
    } for p in plans]}


@router.post("/subscribe")
async def subscribe(data: SubscribeRequest, user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=400, detail="Create a company profile first")

    plan_result = await db.execute(select(Plan).where(Plan.id == data.plan_id, Plan.is_active == True))
    plan = plan_result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if not plan.razorpay_plan_id:
        raise HTTPException(status_code=400, detail="This plan is not available for subscription yet")

    sub_result = await db.execute(select(Subscription).where(Subscription.company_id == company.id))
    existing_sub = sub_result.scalar_one_or_none()

    customer = create_razorpay_customer(company.name, user.email, company.phone)
    rz_sub = create_subscription(plan.razorpay_plan_id, customer["id"])

    if existing_sub:
        existing_sub.plan_id = data.plan_id
        existing_sub.razorpay_sub_id = rz_sub["id"]
        existing_sub.razorpay_customer_id = customer["id"]
        existing_sub.status = "created"
    else:
        sub = Subscription(
            company_id=company.id, plan_id=data.plan_id,
            razorpay_sub_id=rz_sub["id"], razorpay_customer_id=customer["id"],
            status="created", start_date=date.today(),
        )
        db.add(sub)

    company.plan_id = data.plan_id
    await db.commit()
    return {"data": {"checkout_url": rz_sub.get("short_url", ""), "subscription_id": rz_sub["id"]}}


@router.get("/subscribe/status")
async def subscription_status(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="No company found")
    sub_result = await db.execute(select(Subscription).where(Subscription.company_id == company.id))
    sub = sub_result.scalar_one_or_none()
    if not sub:
        return {"data": {"status": "free", "plan": "Free"}}
    plan_result = await db.execute(select(Plan).where(Plan.id == sub.plan_id))
    plan = plan_result.scalar_one_or_none()
    from app.models.product import Product
    from sqlalchemy import func
    product_count = (await db.execute(select(func.count()).where(Product.company_id == company.id, Product.status != "deleted"))).scalar()
    return {"data": {
        "status": sub.status, "plan": plan.name if plan else "Unknown",
        "next_billing_at": sub.next_billing_at.isoformat() if sub.next_billing_at else None,
        "cancel_at_period_end": sub.cancel_at_period_end,
        "products_used": product_count, "max_products": plan.max_products if plan else 5,
    }}


@router.post("/subscribe/cancel")
async def cancel_sub(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    sub_result = await db.execute(select(Subscription).where(Subscription.company_id == company.id))
    sub = sub_result.scalar_one_or_none()
    if not sub or not sub.razorpay_sub_id:
        raise HTTPException(status_code=404, detail="No active subscription")
    cancel_subscription(sub.razorpay_sub_id, cancel_at_cycle_end=True)
    sub.cancel_at_period_end = True
    await db.commit()
    return {"data": {"message": "Subscription will be cancelled at period end"}}


@router.post("/subscribe/reactivate")
async def reactivate_sub(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    sub_result = await db.execute(select(Subscription).where(Subscription.company_id == company.id))
    sub = sub_result.scalar_one_or_none()
    if not sub or not sub.cancel_at_period_end:
        raise HTTPException(status_code=400, detail="No pending cancellation to reactivate")
    sub.cancel_at_period_end = False
    await db.commit()
    return {"data": {"message": "Subscription reactivated"}}


@router.post("/webhook/razorpay")
async def razorpay_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get("X-Razorpay-Signature", "")

    if settings.RAZORPAY_SECRET and not verify_webhook_signature(body, signature, settings.RAZORPAY_SECRET):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    payload = json.loads(body)
    event = payload.get("event", "")
    entity = payload.get("payload", {}).get("subscription", {}).get("entity", {})
    razorpay_sub_id = entity.get("id")

    if not razorpay_sub_id:
        return {"status": "ignored"}

    sub_result = await db.execute(select(Subscription).where(Subscription.razorpay_sub_id == razorpay_sub_id))
    sub = sub_result.scalar_one_or_none()
    if not sub:
        return {"status": "not_found"}

    company_result = await db.execute(select(Company).where(Company.id == sub.company_id))
    company = company_result.scalar_one_or_none()

    if event == "subscription.activated":
        sub.status = "active"
        sub.start_date = date.today()
    elif event == "subscription.charged":
        payment_entity = payload.get("payload", {}).get("payment", {}).get("entity", {})
        sub.last_payment_at = datetime.utcnow()
        sub.amount_paid = payment_entity.get("amount", 0) / 100
        plan_result = await db.execute(select(Plan).where(Plan.id == sub.plan_id))
        plan = plan_result.scalar_one_or_none()
        if company and company.phone and plan:
            await send_subscription_receipt(company.phone, plan.name, float(sub.amount_paid or 0))
    elif event == "subscription.cancelled":
        sub.status = "cancelled"
        sub.cancel_at_period_end = True
    elif event == "subscription.completed":
        sub.status = "expired"
        free_plan = (await db.execute(select(Plan).where(Plan.name == "Free"))).scalar_one_or_none()
        if free_plan and company:
            company.plan_id = free_plan.id
    elif event == "payment.failed":
        sub.status = "past_due"
        plan_result = await db.execute(select(Plan).where(Plan.id == sub.plan_id))
        plan = plan_result.scalar_one_or_none()
        if company and company.phone:
            await send_payment_failed_alert(company.phone, plan.name if plan else "your plan")
    elif event == "subscription.paused":
        sub.status = "paused"

    await db.commit()
    return {"status": "processed"}


@router.get("/invoices")
async def list_invoices(user: User = Depends(require_seller), db: AsyncSession = Depends(get_db)):
    company_result = await db.execute(select(Company).where(Company.user_id == user.id))
    company = company_result.scalar_one_or_none()
    sub_result = await db.execute(select(Subscription).where(Subscription.company_id == company.id))
    sub = sub_result.scalar_one_or_none()
    if not sub or not sub.razorpay_sub_id or not settings.RAZORPAY_KEY_ID:
        return {"data": []}
    import razorpay
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))
    try:
        invoices = client.invoice.all({"subscription_id": sub.razorpay_sub_id})
        return {"data": invoices.get("items", [])}
    except Exception:
        return {"data": []}
