from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Player
from app.security import hash_password, verify_password

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


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
        "South Africa": "ZAF"
    }

    code = country_codes.get(country, "INT")

    return f"DR-{code}-2026-{player_id:06d}"


@router.post("/register")
def register(
    full_name: str = Form(...),
    email: str = Form(...),
    country: str = Form(...),
    alias: str = Form(...),
    password: str = Form(...)
):
    print("========== REGISTER ROUTE HIT ==========")
    print("Full Name:", full_name)
    print("Email:", email)
    print("Country:", country)
    print("Alias:", alias)

    db: Session = SessionLocal()

    try:
        existing_email = (
            db.query(Player)
            .filter(Player.email == email)
            .first()
        )

        if existing_email:
            return {
                "status": "error",
                "message": "Email already registered."
            }

        existing_alias = (
            db.query(Player)
            .filter(Player.alias == alias)
            .first()
        )

        if existing_alias:
            return {
                "status": "error",
                "message": "Player alias already taken."
            }

        player = Player(
            royal_id="TEMP",
            full_name=full_name,
            email=email,
            country=country,
            alias=alias,
            password=hash_password(password),
            xp=0,
            royal_tokens=0,
            level="Explorer",
            badge="Founding Player"
        )

        db.add(player)
        db.commit()
        db.refresh(player)

        player.royal_id = generate_royal_id(
            player.id,
            player.country
        )

        db.commit()

        print("========== PLAYER CREATED ==========")
        print("Royal ID:", player.royal_id)
        print("Player ID:", player.id)

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    finally:
        db.close()


@router.post("/login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    print("========== LOGIN ROUTE HIT ==========")
    print("Email:", email)

    db: Session = SessionLocal()

    try:
        player = (
            db.query(Player)
            .filter(Player.email == email)
            .first()
        )

        if not player:
            return {
                "status": "error",
                "message": "Invalid email or password."
            }

        if not verify_password(password, player.password):
            return {
                "status": "error",
                "message": "Invalid email or password."
            }

        request.session["player_id"] = player.id

        print("========== LOGIN SUCCESS ==========")
        print("Royal ID:", player.royal_id)

        return RedirectResponse(
            url="/dashboard",
            status_code=303
        )

    finally:
        db.close()


@router.get("/logout")
def logout(request: Request):
    request.session.clear()

    return RedirectResponse(
        url="/",
        status_code=303
    )
