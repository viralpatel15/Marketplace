#!/bin/bash
set -e

echo "=== YourMarket Deploy ==="
git pull origin main
docker compose build backend frontend
docker compose up -d
docker exec marketplace-backend-1 alembic upgrade head
echo "=== Deploy complete ==="
docker compose logs --tail=20 backend
