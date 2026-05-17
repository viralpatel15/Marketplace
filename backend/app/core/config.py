from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://admin:strongpass@postgres:5432/marketplace"
    DB_PASSWORD: str = "strongpass"

    REDIS_URL: str = "redis://:redispass@redis:6379/0"
    REDIS_PASSWORD: str = "redispass"

    MEILI_URL: str = "http://meilisearch:7700"
    MEILI_KEY: str = "masterKey123"

    JWT_SECRET: str = "super-long-random-secret-minimum-32-characters"
    JWT_ALGORITHM: str = "HS256"

    MSG91_API_KEY: str = ""
    MSG91_TEMPLATE_ID: str = ""
    GOOGLE_CLIENT_ID: str = ""

    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_SECRET: str = ""

    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_ID: str = ""

    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY: str = ""
    R2_SECRET_KEY: str = ""
    R2_BUCKET: str = "marketplace-images"
    R2_PUBLIC_URL: str = "https://images.yourdomain.in"

    ALLOWED_ORIGINS: str = "http://localhost:3000"
    ENVIRONMENT: str = "development"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
