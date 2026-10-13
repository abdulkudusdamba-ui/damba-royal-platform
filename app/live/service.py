from datetime import datetime, timezone
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.challenges import get_challenge
from app.live.models import LiveRoom


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def require_room_member(
    db: Session,
    room_code: str,
    player_id: int
) -> LiveRoom:
    room = db.query(LiveRoom).filter(
        LiveRoom.room_code == room_code.upper()
    ).first()

    if not room:
        raise HTTPException(status_code=404, detail="Room not found.")

    if player_id not in (room.host_player_id, room.guest_player_id):
        raise HTTPException(status_code=403, detail="Room access denied.")

    return room


def finalize_room(db: Session, room: LiveRoom) -> bool:
    if room.status != "active":
        return room.status == "complete"

    both_answered = (
        room.host_answer is not None
        and room.guest_answer is not None
    )
    deadline_passed = (
        room.deadline_at is not None
        and utcnow() >= room.deadline_at
    )

    if not both_answered and not deadline_passed:
        return False

    challenge = get_challenge(room.challenge_id)
    if challenge is None:
        room.status = "complete"
        db.commit()
        return True

    room.host_correct = room.host_answer == challenge["correct_answer"]
    room.guest_correct = room.guest_answer == challenge["correct_answer"]
    scoring = challenge.get("score", {})
    base_points = int(scoring.get("correct", 50))
    bonus_rate = float(scoring.get("time_bonus", 0))
    bonus_cap = int(scoring.get("max_time_bonus", 0))

    def score(correct: bool, answered_at: Optional[datetime]) -> int:
        if not correct:
            return 0
        remaining = max(
            0,
            (room.deadline_at - answered_at).total_seconds()
        ) if answered_at and room.deadline_at else 0
        time_bonus = min(bonus_cap, int(remaining * bonus_rate))
        return base_points + time_bonus

    room.host_score = score(room.host_correct, room.host_answered_at)
    room.guest_score = score(room.guest_correct, room.guest_answered_at)
    room.status = "complete"
    db.commit()
    return True
