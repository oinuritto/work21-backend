#!/bin/bash
set -e

echo "Waiting for database..."
MAX_RETRIES=30
RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
  if python -c "
import sys
from urllib.parse import urlparse
try:
    import psycopg2
    db_url = '${DATABASE_URL}'
    db_url = db_url.replace('+asyncpg', '').replace('postgresql+asyncpg://', 'postgresql://')
    parsed = urlparse(db_url)
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:] if parsed.path else 'postgres',
        connect_timeout=2
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
    echo "Database is ready!"
    break
  fi
  
  RETRY=$((RETRY + 1))
  if [ $RETRY -lt $MAX_RETRIES ]; then
    echo "Database unavailable - retrying... ($RETRY/$MAX_RETRIES)"
    sleep 2
  else
    echo "ERROR: Database not available"
    exit 1
  fi
done

echo "Running Alembic migrations..."
if alembic upgrade head; then
    echo "Migrations completed."
else
    echo "Warning: Migration failed. Continuing..."
fi

echo "Starting application..."
exec "$@"