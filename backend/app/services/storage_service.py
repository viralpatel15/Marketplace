import boto3
from uuid import uuid4
from app.core.config import settings

r2_client = boto3.client(
    "s3",
    endpoint_url=f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com",
    aws_access_key_id=settings.R2_ACCESS_KEY,
    aws_secret_access_key=settings.R2_SECRET_KEY,
)


async def upload_file(file_bytes: bytes, filename: str, folder: str, content_type: str = "image/jpeg") -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    key = f"{folder}/{uuid4()}.{ext}"

    if settings.R2_ACCESS_KEY:
        r2_client.put_object(
            Bucket=settings.R2_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    else:
        print(f"[DEV] Would upload {key} to R2 (not configured)")

    return f"{settings.R2_PUBLIC_URL}/{key}"


async def delete_file(url: str):
    if not settings.R2_ACCESS_KEY:
        return
    key = url.replace(f"{settings.R2_PUBLIC_URL}/", "")
    r2_client.delete_object(Bucket=settings.R2_BUCKET, Key=key)
