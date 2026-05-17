import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_addr
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.routers import auth, companies, products, categories, inquiries, subscriptions, analytics, admin, sitemap

limiter = Limiter(key_func=get_remote_addr)

app = FastAPI(
    title="Marketplace API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start) * 1000)
    print(f"[{request_id}] {request.method} {request.url.path} → {response.status_code} ({duration_ms}ms)")
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(auth.router,          prefix="/api/auth",         tags=["Auth"])
app.include_router(companies.router,     prefix="/api/companies",    tags=["Companies"])
app.include_router(products.router,      prefix="/api/products",     tags=["Products"])
app.include_router(categories.router,    prefix="/api/categories",   tags=["Categories"])
app.include_router(inquiries.router,     prefix="/api",              tags=["Inquiries"])
app.include_router(subscriptions.router, prefix="/api",              tags=["Subscriptions"])
app.include_router(analytics.router,     prefix="/api/analytics",    tags=["Analytics"])
app.include_router(admin.router,         prefix="/api/admin",        tags=["Admin"])
app.include_router(sitemap.router,       prefix="/api",              tags=["Sitemap"])


@app.get("/health")
async def health():
    from app.core.database import engine
    import redis.asyncio as aioredis
    import meilisearch

    db_status = "unknown"
    redis_status = "unknown"
    meili_status = "unknown"

    try:
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    try:
        r = aioredis.from_url(settings.REDIS_URL)
        await r.ping()
        await r.aclose()
        redis_status = "connected"
    except Exception:
        redis_status = "error"

    try:
        client = meilisearch.Client(settings.MEILI_URL, settings.MEILI_KEY)
        client.health()
        meili_status = "connected"
    except Exception:
        meili_status = "error"

    return {
        "status": "ok",
        "database": db_status,
        "redis": redis_status,
        "meilisearch": meili_status,
        "version": "1.0.0",
    }
