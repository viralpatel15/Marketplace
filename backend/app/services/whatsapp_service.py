import httpx
from app.core.config import settings


async def send_whatsapp_template(phone: str, template_name: str, components: list):
    if not settings.WHATSAPP_TOKEN:
        print(f"[DEV] WhatsApp to {phone} | template: {template_name}")
        return

    url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": f"91{phone}",
        "type": "template",
        "template": {"name": template_name, "language": {"code": "en"}, "components": components},
    }
    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload, headers={"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"})


async def send_lead_notification(seller_phone: str, buyer_name: str, product_name: str, quantity: int):
    await send_whatsapp_template(seller_phone, "new_lead_received", [
        {"type": "body", "parameters": [
            {"type": "text", "text": buyer_name},
            {"type": "text", "text": product_name},
            {"type": "text", "text": str(quantity or 1)},
        ]}
    ])


async def send_inquiry_confirmation(buyer_phone: str, product_name: str, company_name: str):
    await send_whatsapp_template(buyer_phone, "inquiry_confirmation", [
        {"type": "body", "parameters": [
            {"type": "text", "text": product_name},
            {"type": "text", "text": company_name},
        ]}
    ])


async def send_subscription_receipt(seller_phone: str, plan_name: str, amount: float):
    await send_whatsapp_template(seller_phone, "subscription_receipt", [
        {"type": "body", "parameters": [
            {"type": "text", "text": plan_name},
            {"type": "text", "text": f"Rs. {amount:.0f}"},
        ]}
    ])


async def send_payment_failed_alert(seller_phone: str, plan_name: str):
    await send_whatsapp_template(seller_phone, "payment_failed_alert", [
        {"type": "body", "parameters": [{"type": "text", "text": plan_name}]}
    ])
