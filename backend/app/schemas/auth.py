from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=8)
    role: str = Field(default="buyer", pattern="^(buyer|seller)$")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class OTPRequest(BaseModel):
    phone: str
    otp: str = Field(..., min_length=6, max_length=6)


class SendOTPRequest(BaseModel):
    phone: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    phone: str


class ResetPasswordRequest(BaseModel):
    phone: str
    otp: str
    new_password: str = Field(..., min_length=8)


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    role: str
    is_verified: bool
    avatar_url: Optional[str]

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    user: UserResponse
    access_token: str
    refresh_token: str
    message: Optional[str] = None
