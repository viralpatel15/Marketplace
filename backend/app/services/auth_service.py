import httpx
import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests

from app.core.config import settings
from app.core.security import hash_password, verify_password, generate_otp, create_access_token, create_refresh_token
from app.models.user import User


def get_redis():
    return aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def store_otp_redis(phone: str, otp: str):
    r = get_redis()
    await r.setex(f"otp:{phone}", 600, otp)
    await r.aclose()


async def verify_otp_redis(phone: str, otp: str) -> bool:
    r = get_redis()
    stored = await r.get(f"otp:{phone}")
    if stored == otp:
        await r.delete(f"otp:{phone}")
        await r.aclose()
        return True
    await r.aclose()
    return False


async def store_refresh_token(user_id: int, token: str):
    r = get_redis()
    await r.setex(f"refresh:{user_id}", 604800, token)
    await r.aclose()


async def invalidate_refresh_token(user_id: int):
    r = get_redis()
    await r.delete(f"refresh:{user_id}")
    await r.aclose()


async def send_otp_msg91(phone: str, otp: str):
    if not settings.MSG91_API_KEY:
        print(f"[DEV] OTP for {phone}: {otp}")
        return
    async with httpx.AsyncClient() as client:
        await client.post(
            "https://api.msg91.com/api/v5/otp",
            json={"template_id": settings.MSG91_TEMPLATE_ID, "mobile": f"91{phone}", "otp": otp},
            headers={"authkey": settings.MSG91_API_KEY},
        )


async def register_user(data, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    if data.phone:
        result2 = await db.execute(select(User).where(User.phone == data.phone))
        if result2.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Phone already registered")

    user = User(
        name=data.name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    otp = generate_otp()
    await store_otp_redis(data.phone, otp)
    await send_otp_msg91(data.phone, otp)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    await store_refresh_token(user.id, refresh_token)

    return user, access_token, refresh_token


async def login_user(email: str, password: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user or not user.password_hash or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    from datetime import datetime
    user.last_login = datetime.utcnow()
    await db.commit()

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    await store_refresh_token(user.id, refresh_token)

    return user, access_token, refresh_token


async def verify_otp_and_activate(phone: str, otp: str, db: AsyncSession):
    if not await verify_otp_redis(phone, otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    result = await db.execute(select(User).where(User.phone == phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    await db.commit()
    return user


async def google_login(id_token_str: str, db: AsyncSession):
    try:
        info = google_id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), settings.GOOGLE_CLIENT_ID
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Google token")

    google_id = info["sub"]
    email = info["email"]
    name = info.get("name", "")
    avatar_url = info.get("picture")

    result = await db.execute(select(User).where(User.google_id == google_id))
    user = result.scalar_one_or_none()

    if not user:
        result2 = await db.execute(select(User).where(User.email == email))
        user = result2.scalar_one_or_none()
        if user:
            user.google_id = google_id
            user.avatar_url = avatar_url or user.avatar_url
        else:
            user = User(name=name, email=email, google_id=google_id, avatar_url=avatar_url, is_verified=True, role="buyer")
            db.add(user)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(user.id, user.role)
    refresh_token = create_refresh_token(user.id)
    await store_refresh_token(user.id, refresh_token)
    return user, access_token, refresh_token
