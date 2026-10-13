from datetime import timedelta
import secrets

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.challenges import get_all_challenges, get_challenge
from app.csrf import csrf_token, verify_csrf
from app.database import SessionLocal
from app.live.models import LiveRoom
from app.live.service import finalize_room, require_room_member, utcnow
from app.models import Player

router = APIRouter(tags=["Live match"])
templates = Jinja2Templates(directory="app/templates")


def _player_id(request: Request) -> int:
    player_id = request.session.get("player_id")
    if not player_id:
        raise HTTPException(status_code=401, detail="Authentication required.")
    return int(player_id)


def _public_challenge(challenge: dict) -> dict:
    return {
        "id": challenge["id"],
        "title": challenge["title"],
        "category": challenge["category"],
        "description": challenge["description"],
        "instruction": challenge["instruction"],
        "target": challenge.get("target"),
        "display_sequence": challenge.get("display_sequence"),
        "memory_sequence": challenge.get("memory_sequence"),
        "options": challenge.get("options", []),
        "time_limit": int(challenge.get("time_limit", 60))
    }


@router.post("/api/live/rooms/{room_code}/start")
def start_match(request: Request, room_code: str):
    verify_csrf(request)
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, player_id)
        if player_id != room.host_player_id:
            raise HTTPException(status_code=403, detail="Only the host may start.")
        if room.status != "lobby":
            raise HTTPException(status_code=409, detail="Match cannot be started.")
        if (
            room.guest_player_id is None
            or room.guest_player_id == room.host_player_id
            or not room.host_ready
            or not room.guest_ready
        ):
            raise HTTPException(
                status_code=409,
                detail="Exactly two players must be present and ready."
            )

        challenge = secrets.choice(get_all_challenges())
        started_at = utcnow()
        deadline_at = started_at + timedelta(
            seconds=int(challenge.get("time_limit", 60))
        )
        updated = db.query(LiveRoom).filter(
            LiveRoom.room_code == room.room_code,
            LiveRoom.host_player_id == player_id,
            LiveRoom.status == "lobby",
            LiveRoom.guest_player_id.is_not(None),
            LiveRoom.guest_player_id != LiveRoom.host_player_id,
            LiveRoom.host_ready.is_(True),
            LiveRoom.guest_ready.is_(True)
        ).update(
            {
                LiveRoom.challenge_id: challenge["id"],
                LiveRoom.started_at: started_at,
                LiveRoom.deadline_at: deadline_at,
                LiveRoom.status: "active"
            },
            synchronize_session=False
        )
        if updated != 1:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail="Exactly two players must be present and ready."
            )
        db.commit()
        return {"status": "active", "match_url": f"/live/{room.room_code}/match"}
    finally:
        db.close()


@router.get("/live/{room_code}/match", response_class=HTMLResponse)
def live_match_page(request: Request, room_code: str):
    player_id = request.session.get("player_id")
    if not player_id:
        return RedirectResponse(url="/login", status_code=303)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, int(player_id))
        if room.status == "lobby":
            return RedirectResponse(
                url=f"/live/{room.room_code}",
                status_code=303
            )
        return templates.TemplateResponse(
            request=request,
            name="live_match.html",
            context={"room_code": room.room_code, "csrf": csrf_token(request)}
        )
    finally:
        db.close()


@router.get("/api/live/rooms/{room_code}/match")
def get_match_state(request: Request, room_code: str):
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, player_id)
        if room.status == "lobby":
            raise HTTPException(status_code=409, detail="The match has not started.")

        is_complete = finalize_room(db, room)
        db.refresh(room)
        challenge = get_challenge(room.challenge_id)
        if challenge is None:
            raise HTTPException(status_code=409, detail="Challenge is unavailable.")

        host = db.query(Player).filter(
            Player.id == room.host_player_id
        ).first()
        guest = db.query(Player).filter(
            Player.id == room.guest_player_id
        ).first()
        is_host = player_id == room.host_player_id
        own_answer = room.host_answer if is_host else room.guest_answer
        opponent_answer = room.guest_answer if is_host else room.host_answer

        result = {
            "room_code": room.room_code,
            "status": room.status,
            "deadline_at": (
                room.deadline_at.isoformat() + "Z"
                if room.deadline_at else None
            ),
            "players": [
                {
                    "alias": host.alias if host else "Player",
                    "score": room.host_score if is_complete else None,
                    "is_you": is_host
                },
                {
                    "alias": guest.alias if guest else "Player",
                    "score": room.guest_score if is_complete else None,
                    "is_you": not is_host
                }
            ],
            "challenge": _public_challenge(challenge),
            "submitted_by_you": own_answer is not None,
            "waiting_for_opponent": (
                room.status == "active" and own_answer is not None
            )
        }

        if room.status == "active":
            result["seconds_remaining"] = max(
                0,
                int((room.deadline_at - utcnow()).total_seconds())
            )
        elif is_complete:
            result["result"] = {
                "correct_answer": challenge["correct_answer"],
                "your_answer": own_answer,
                "your_correct": (
                    room.host_correct if is_host else room.guest_correct
                ),
                "opponent_answered": opponent_answer is not None,
                "your_score": (
                    room.host_score if is_host else room.guest_score
                ),
                "opponent_score": (
                    room.guest_score if is_host else room.host_score
                ),
                "points_available": int(
                    challenge.get("score", {}).get("correct", 50)
                ) + int(
                    challenge.get("score", {}).get("max_time_bonus", 0)
                )
            }
        return result
    finally:
        db.close()


@router.post("/api/live/rooms/{room_code}/answer")
def submit_match_answer(
    request: Request,
    room_code: str,
    answer: str = Form(...)
):
    verify_csrf(request)
    player_id = _player_id(request)
    db = SessionLocal()
    try:
        room = require_room_member(db, room_code, player_id)
        if room.status != "active":
            raise HTTPException(status_code=409, detail="The round is not accepting answers.")
        if utcnow() >= room.deadline_at:
            finalize_room(db, room)
            raise HTTPException(status_code=409, detail="The round deadline has passed.")

        challenge = get_challenge(room.challenge_id)
        if challenge is None:
            raise HTTPException(status_code=409, detail="Challenge is unavailable.")
        valid_options = {
            str(option["id"])
            for option in challenge.get("options", [])
        }
        submitted_answer = answer.strip()
        if not submitted_answer or submitted_answer not in valid_options:
            raise HTTPException(status_code=422, detail="Choose a listed answer.")

        is_host = player_id == room.host_player_id
        answer_field = "host_answer" if is_host else "guest_answer"
        answered_at_field = (
            "host_answered_at" if is_host else "guest_answered_at"
        )
        answer_column = getattr(LiveRoom, answer_field)
        answered_at_column = getattr(LiveRoom, answered_at_field)
        answered_at = utcnow()
        updated = db.query(LiveRoom).filter(
            LiveRoom.room_code == room.room_code,
            LiveRoom.status == "active",
            answer_column.is_(None),
            LiveRoom.deadline_at > utcnow()
        ).update(
            {
                answer_column: submitted_answer,
                answered_at_column: answered_at
            },
            synchronize_session=False
        )
        if updated != 1:
            db.rollback()
            db.refresh(room)
            if room.status == "active" and utcnow() >= room.deadline_at:
                finalize_room(db, room)
                raise HTTPException(
                    status_code=409,
                    detail="The round deadline has passed."
                )
            raise HTTPException(
                status_code=409,
                detail="Your answer was already submitted."
            )
        db.commit()
        db.refresh(room)
        is_complete = finalize_room(db, room)
        return {
            "submitted": True,
            "status": "complete" if is_complete else "active"
        }
    finally:
        db.close()
