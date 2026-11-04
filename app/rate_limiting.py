import hashlib
import os
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import case, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.database import engine
from app.models import RateLimitBucket


DEFAULT_POLICIES = {
    "login": (5, 60),
    "registration": (3, 3600),
    "enquiry": (5, 3600),
    "room_create": (5, 3600),
    "room_join": (20, 60),
    "challenge_submission": (30, 60),
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _policy(action: str) -> tuple[int, int]:
    default_limit, default_window = DEFAULT_POLICIES[action]
    prefix = f"RATE_LIMIT_{action.upper()}"
    return (
        int(os.getenv(f"{prefix}_MAX", default_limit)),
        int(os.getenv(f"{prefix}_WINDOW_SECONDS", default_window)),
    )


def _action_for(request: Request) -> str | None:
    if request.method != "POST":
        return None

    path = request.url.path.rstrip("/")
    if path == "/auth/login":
        return "login"
    if path == "/auth/register":
        return "registration"
    if path == "/api/enquiries":
        return "enquiry"
    if path == "/api/live/rooms":
        return "room_create"
    if path.startswith("/api/live/rooms/") and path.endswith("/join"):
        return "room_join"
    if path.startswith("/api/challenges/") and path.endswith("/complete"):
        return "challenge_submission"
    return None


def _consume(key: str, window_seconds: int) -> tuple[int, datetime]:
    table = RateLimitBucket.__table__
    now = _utcnow()
    cutoff = now - timedelta(seconds=window_seconds)
    expires_at = now + timedelta(seconds=window_seconds)
    dialect = engine.dialect.name
    if dialect == "sqlite":
        insert = sqlite_insert(table)
    elif dialect == "postgresql":
        insert = postgresql_insert(table)
    else:
        raise RuntimeError("Rate limiting requires SQLite or PostgreSQL.")

    expired = table.c.window_started <= cutoff
    statement = insert.values(
        bucket_key=key,
        window_started=now,
        request_count=1,
        expires_at=expires_at,
    ).on_conflict_do_update(
        index_elements=[table.c.bucket_key],
        set_={
            "request_count": case(
                (expired, 1),
                else_=table.c.request_count + 1,
            ),
            "window_started": case(
                (expired, now),
                else_=table.c.window_started,
            ),
            "expires_at": case(
                (expired, expires_at),
                else_=table.c.expires_at,
            ),
        },
    )

    with engine.begin() as connection:
        connection.execute(statement)
        result = connection.execute(
            select(table.c.request_count, table.c.window_started).where(
                table.c.bucket_key == key
            )
        ).one()
    return result.request_count, result.window_started


def check_rate_limit(request: Request, action: str) -> int | None:
    limit, window_seconds = _policy(action)
    if limit < 1 or window_seconds < 1:
        raise RuntimeError("Rate limit settings must be positive integers.")

    client_host = request.client.host if request.client else "unknown"
    bucket_key = hashlib.sha256(
        f"{action}:{client_host}".encode("utf-8")
    ).hexdigest()
    count, window_started = _consume(bucket_key, window_seconds)
    if count <= limit:
        return None

    retry_after = int(
        max(
            1,
            (window_started + timedelta(seconds=window_seconds) - _utcnow())
            .total_seconds(),
        )
    )
    return retry_after


def action_for_request(request: Request) -> str | None:
    return _action_for(request)
