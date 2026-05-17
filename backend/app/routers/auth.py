from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import generate_otp, create_access_token, create_refresh_token, verify_token, hash_password
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import (
    RegisterRequest, LoginRequest, OTPRequest, SendOTPRequest,
    GoogleAuthRequest, RefreshRequest, ForgotPasswordRequest, ResetPasswordRequest,
    TokenResponse, UserResponse
)
from app.services.auth_service import (
    register_user, login_user, verify_otp_and_activate, google_login,
    store_otp_redis, verify_otp_redis, store_refresh_token, invalidate_refresh_token, send_otp_msg91
)
from fastapi import HTTPException

router = APIRouter()


@router.post("/register", status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await register_user(data, db)
    return {"data": {"user": UserResponse.model_validate(user), "access_token": access_token,
                     "refresh_token": refresh_token, "message": f"OTP sent to {data.phone}"}}


@router.post("/login")
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await login_user(data.email, data.password, db)
    return {"data": {"user": UserResponse.model_validate(user), "access_token": access_token,
                     "refresh_token": refresh_token}}


@router.post("/verify-otp")
async def verify_otp(data: OTPRequest, db: AsyncSession = Depends(get_db)):
    user = await verify_otp_and_activate(data.phone, data.otp, db)
    return {"data": {"message": "Phone verified successfully", "user": UserResponse.model_validate(user)}}


@router.post("/send-otp")
async def send_otp(data: SendOTPRequest):
    otp = generate_otp()
    await store_otp_redis(data.phone, otp)
    await send_otp_msg91(data.phone, otp)
    return {"data": {"message": "OTP sent"}}


@router.post("/google")
async def google_auth(data: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    user, access_token, refresh_token = await google_login(data.id_token, db)
    return {"data": {"user": UserResponse.model_validate(user), "access_token": access_token,
                     "refresh_token": refresh_token}}


@router.post("/refresh")
async def refresh(data: RefreshRequest):
    payload = verify_token(data.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    user_id = int(payload["sub"])
    access_token = create_access_token(user_id, "buyer")
    return {"data": {"access_token": access_token}}


@router.post("/logout")
async def logout(user: User = Depends(get_current_user)):
    await invalidate_refresh_token(user.id)
    return {"data": {"message": "Logged out successfully"}}


@router.post("/forgot-password")
async def forgot_password(data: ForgotPasswordRequest):
    otp = generate_otp()
    await store_otp_redis(data.phone, otp)
    await send_otp_msg91(data.phone, otp)
    return {"data": {"message": "Password reset OTP sent"}}


@router.post("/reset-password")
async def reset_password(data: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if not await verify_otp_redis(data.phone, data.otp):
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    result = await db.execute(select(User).where(User.phone == data.phone))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.password_hash = hash_password(data.new_password)
    await db.commit()
    return {"data": {"message": "Password reset successful"}}
