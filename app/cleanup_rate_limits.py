from datetime import datetime, timezone

from sqlalchemy import delete

from app.database import engine
from app.models import RateLimitBucket


def cleanup_expired_buckets() -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with engine.begin() as connection:
        result = connection.execute(
            delete(RateLimitBucket).where(RateLimitBucket.expires_at <= now)
        )
        return result.rowcount or 0


if __name__ == "__main__":
    print(cleanup_expired_buckets())
