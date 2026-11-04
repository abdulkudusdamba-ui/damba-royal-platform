import secrets

from fastapi import HTTPException, Request


def csrf_token(request: Request) -> str:
    token = request.session.get("csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        request.session["csrf"] = token
    return token


def verify_csrf(request: Request, token: str = "") -> None:
    expected = request.session.get("csrf")
    supplied = token or request.headers.get("x-csrf-token", "")
    if not expected or not secrets.compare_digest(expected, supplied):
        raise HTTPException(status_code=403, detail="Invalid form token.")
