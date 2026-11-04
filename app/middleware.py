from urllib.parse import urlsplit

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.rate_limiting import action_for_request, check_rate_limit


class OriginCSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            source = request.headers.get("origin") or request.headers.get("referer")
            host = request.headers.get("host", "").lower()
            try:
                parsed = urlsplit(source) if source else None
            except ValueError:
                parsed = None
            if (
                parsed is None
                or parsed.scheme not in {"http", "https"}
                or parsed.scheme != request.url.scheme
                or parsed.netloc.lower() != host
            ):
                return JSONResponse(
                    {"detail": "Request origin could not be verified."},
                    status_code=403,
                )
        return await call_next(request)


class SharedRateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        action = action_for_request(request)
        if action is not None:
            try:
                retry_after = check_rate_limit(request, action)
            except (RuntimeError, ValueError, SQLAlchemyError):
                return JSONResponse(
                    {"detail": "Rate limiting is temporarily unavailable."},
                    status_code=503,
                )
            if retry_after is not None:
                return JSONResponse(
                    {"detail": "Too many requests. Please try again later."},
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )
        return await call_next(request)
