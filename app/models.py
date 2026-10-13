from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
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

    level = Column(String, default="Explorer")
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



class NewsPost(Base):
    __tablename__ = "news_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String, nullable=False, default="General")
    published = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CatalogItem(Base):
    """Livestock listings and Damba Royal Luxury products."""

    __tablename__ = "catalog_items"

    id = Column(Integer, primary_key=True, index=True)
    section = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="")
    description = Column(Text, nullable=False, default="")
    price_note = Column(String, nullable=False, default="")
    status = Column(String, nullable=False, default="available")
    published = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False, index=True)
    section = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False, default="")
    message = Column(Text, nullable=False)
    contact = Column(String, nullable=False, default="")
    item_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
