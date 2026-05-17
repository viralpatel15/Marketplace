import hmac
import hashlib
import razorpay
from app.core.config import settings


def get_razorpay_client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_SECRET))


def create_razorpay_customer(name: str, email: str, phone: str) -> dict:
    if not settings.RAZORPAY_KEY_ID:
        return {"id": "cust_test123"}
    client = get_razorpay_client()
    return client.customer.create({"name": name, "email": email, "contact": phone})


def create_subscription(razorpay_plan_id: str, customer_id: str, total_count: int = 120) -> dict:
    if not settings.RAZORPAY_KEY_ID:
        return {"id": "sub_test123", "short_url": "https://rzp.io/test"}
    client = get_razorpay_client()
    return client.subscription.create({
        "plan_id": razorpay_plan_id,
        "customer_notify": 1,
        "total_count": total_count,
        "customer_id": customer_id,
    })


def cancel_subscription(razorpay_sub_id: str, cancel_at_cycle_end: bool = True):
    if not settings.RAZORPAY_KEY_ID:
        return
    client = get_razorpay_client()
    client.subscription.cancel(razorpay_sub_id, {"cancel_at_cycle_end": 1 if cancel_at_cycle_end else 0})


def verify_webhook_signature(payload_bytes: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
