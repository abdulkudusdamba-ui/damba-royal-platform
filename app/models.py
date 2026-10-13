from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime

from app.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    royal_id = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    country = Column(String, nullable=False)
    alias = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

    xp = Column(Integer, default=0)
    royal_tokens = Column(Integer, default=0)

    level = Column(String, default="Unranked")
    badge = Column(String, default="Founding Player")


class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)

    player_id = Column(
        Integer,
        ForeignKey("players.id"),
        nullable=False,
        index=True
    )

    challenge_id = Column(
        String,
        nullable=False,
        index=True
    )

    answer = Column(
        String,
        nullable=False
    )

    correct = Column(
        Integer,
        nullable=False,
        default=0
    )

    score = Column(
        Integer,
        nullable=False,
        default=0
    )

    xp_awarded = Column(
        Integer,
        nullable=False,
        default=0
    )

    tokens_awarded = Column(
        Integer,
        nullable=False,
        default=0
    )

    completed_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "player_id",
            "challenge_id",
            name="uq_player_challenge"
        ),
    )
