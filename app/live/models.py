from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class LiveRoom(Base):
    __tablename__ = "live_rooms"

    room_code = Column(String(6), primary_key=True, index=True)
    host_player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False
    )
    guest_player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=True
    )
    status = Column(String, nullable=False, default="lobby")
    host_ready = Column(Boolean, nullable=False, default=False)
    guest_ready = Column(Boolean, nullable=False, default=False)
    challenge_id = Column(String, nullable=True)
    started_at = Column(DateTime, nullable=True)
    deadline_at = Column(DateTime, nullable=True)
    host_answer = Column(String, nullable=True)
    guest_answer = Column(String, nullable=True)
    host_answered_at = Column(DateTime, nullable=True)
    guest_answered_at = Column(DateTime, nullable=True)
    host_score = Column(Integer, nullable=False, default=0)
    guest_score = Column(Integer, nullable=False, default=0)
    host_correct = Column(Boolean, nullable=True)
    guest_correct = Column(Boolean, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
