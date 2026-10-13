from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Player
from app.security import hash_password, verify_password


router = APIRouter(prefix="/auth", tags=["Authentication"])
DUMMY_PASSWORD_HASH = hash_password("invalid-login-placeholder")


def generate_royal_id(player_id: int, country: str):
    country_codes = {
        "Ghana": "GHA",
        "Nigeria": "NGA",
        "United States": "USA",
        "United Kingdom": "GBR",
        "Canada": "CAN",
        "Philippines": "PHL",
        "Japan": "JPN",
        "Germany": "DEU",
        "Brazil": "BRA",
        "South Africa": "ZAF",
    }
    code = country_codes.get(country, "INT")
    return f"DR-{code}-2026-{player_id:06d}"


@router.post("/register")
def register(
    full_name: str = Form(...),
    email: str = Form(...),
    country: str = Form(...),
    alias: str = Form(...),
    password: str = Form(...),
):
    db: Session = SessionLocal()
    try:
        player = Player(
            full_name=full_name.strip(),
            email=email.strip().lower(),
            country=country,
            alias=alias.strip(),
            xp=0,
            royal_tokens=0,
            level="Explorer",
            badge="Founding Player",
        )
        setattr(player, "password", hash_password(password))
        db.add(player)
        db.flush()
        player.royal_id = generate_royal_id(player.id, player.country)
        db.commit()
    except ValueError:
        db.rollback()
        raise HTTPException(status_code=422, detail="Invalid registration details.")
    except IntegrityError:
        db.rollback()
    finally:
        db.close()

    return RedirectResponse(url="/login", status_code=303)


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    db: Session = SessionLocal()
    try:
        player = (
            db.query(Player)
            .filter(func.lower(Player.email) == email.strip().lower())
            .first()
        )
        stored_password = player.password if player else DUMMY_PASSWORD_HASH
        if not verify_password(password, stored_password) or not player:
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password.",
            )

        request.session.clear()
        request.session["player_id"] = player.id
        return RedirectResponse(url="/dashboard", status_code=303)
    finally:
        db.close()


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
