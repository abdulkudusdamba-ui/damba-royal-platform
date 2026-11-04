import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal
from app.csrf import csrf_token, verify_csrf
from app.live.models import LiveRoom
from app.live.service import require_room_member
from app.models import Player

router = APIRouter(tags=["Live competition"])
templates = Jinja2Templates(directory="app/templates")
ROOM_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _player_id(request: Request) -> int:
    player_id = request.session.get("player_id")
    if not player_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return int(player_id)


@router.get("/live", response_class=HTMLResponse)
def live_lobby_page(request: Request):
    if not request.session.get("player_id"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="live.html",
        context={"csrf": csrf_token(request)}
    )


@router.get("/live/{room_code}", response_class=HTMLResponse)
def live_room_page(request: Request, room_code: str):
    player_id = request.session.get("player_id")
    if not player_id:
        return RedirectResponse(url="/login", status_code=303)

    db = SessionLocal()
    try:
        require_room_member(db, room_code, int(player_id))
        return templates.TemplateResponse(
            request=request,
            name="live.html",
            context={"room_code": room_code.upper(), "csrf": csrf_token(request)}
        )
    finally:
        db.close()


@router.post("/api/live/rooms")
def create_room(request: Request):
    verify_csrf(request)
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        if not db.query(Player.id).filter(Player.id == player_id).first():
            request.session.clear()
            raise HTTPException(status_code=401, detail="Authentication required.")

        for _ in range(5):
            room_code = "".join(
                secrets.choice(ROOM_ALPHABET) for _ in range(6)
            )
            if not db.query(LiveRoom).filter(
                LiveRoom.room_code == room_code
            ).first():
                room = LiveRoom(
                    room_code=room_code,
                    host_player_id=player_id
                )
                db.add(room)
                db.commit()
                return {
                    "room_code": room_code,
                    "room_url": f"/live/{room_code}"
                }
        raise HTTPException(
            status_code=503,
            detail="Unable to create a unique room code. Try again."
        )
    finally:
        db.close()


@router.post("/api/live/rooms/join")
def join_room(request: Request, room_code: str = Form(...)):
    verify_csrf(request)
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        code = room_code.strip().upper()
        room = db.query(LiveRoom).filter(
            LiveRoom.room_code == code
        ).first()
        if not room:
            raise HTTPException(status_code=404, detail="Room not found.")
        if player_id == room.host_player_id:
            raise HTTPException(
                status_code=409,
                detail="The room host cannot join as the second player."
            )
        if room.status != "lobby":
            raise HTTPException(
                status_code=409,
                detail="This competition has already started."
            )
        if room.guest_player_id not in (None, player_id):
            raise HTTPException(status_code=409, detail="Room is full.")

        updated = db.query(LiveRoom).filter(
            LiveRoom.room_code == code,
            LiveRoom.status == "lobby",
            LiveRoom.guest_player_id.is_(None)
        ).update(
            {LiveRoom.guest_player_id: player_id},
            synchronize_session=False
        )
        if updated != 1 and room.guest_player_id != player_id:
            db.rollback()
            raise HTTPException(status_code=409, detail="Room is full.")
        db.commit()
        return {"room_code": code, "room_url": f"/live/{code}"}
    finally:
        db.close()


@router.get("/api/live/rooms/{room_code}")
def get_room_state(request: Request, room_code: str):
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, player_id)
        host = db.query(Player).filter(
            Player.id == room.host_player_id
        ).first()
        guest = db.query(Player).filter(
            Player.id == room.guest_player_id
        ).first() if room.guest_player_id else None

        return {
            "room_code": room.room_code,
            "status": room.status,
            "players": [
                {
                    "alias": host.alias if host else "Player",
                    "ready": room.host_ready,
                    "is_you": player_id == room.host_player_id
                },
                *([{
                    "alias": guest.alias,
                    "ready": room.guest_ready,
                    "is_you": player_id == room.guest_player_id
                }] if guest else [])
            ],
            "player_count": 1 + int(guest is not None),
            "can_start": (
                player_id == room.host_player_id
                and room.status == "lobby"
                and guest is not None
                and room.host_ready
                and room.guest_ready
            )
        }
    finally:
        db.close()


@router.post("/api/live/rooms/{room_code}/ready")
def set_ready(request: Request, room_code: str):
    verify_csrf(request)
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, player_id)
        if room.status != "lobby":
            raise HTTPException(
                status_code=409,
                detail="The lobby is no longer accepting readiness changes."
            )
        if player_id == room.host_player_id:
            room.host_ready = True
        elif room.guest_player_id == player_id:
            room.guest_ready = True
        else:
            raise HTTPException(status_code=403, detail="Room access denied.")
        db.commit()
        return {"ready": True}
    finally:
        db.close()
