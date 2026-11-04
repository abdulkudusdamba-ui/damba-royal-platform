from concurrent.futures import ThreadPoolExecutor
import os
import secrets
import subprocess
import sys

from sqlalchemy import inspect, select

from app.database import SessionLocal, engine
from app.initialize import initialize_database
from app.models import Player


def test_repeated_initialization_preserves_existing_rows():
    with SessionLocal() as session:
        player = Player(
            full_name="Existing User",
            email="existing@example.test",
            country="Ghana",
            alias="existing-player",
            royal_id="DR-GHA-2026-000001",
        )
        player.password = "test-password-hash"
        session.add(player)
        session.commit()
        player_id = player.id

    initialize_database()
    initialize_database()

    with SessionLocal() as session:
        preserved = session.get(Player, player_id)
        assert preserved is not None
        assert preserved.email == "existing@example.test"
        assert session.scalar(
            select(Player.id).where(Player.id == player_id)
        ) == player_id

    assert "rate_limit_buckets" in inspect(engine).get_table_names()


def test_importing_app_does_not_create_a_database(tmp_path):
    database_path = tmp_path / "not-created.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"
    imported = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )

    assert imported.returncode == 0, imported.stderr
    assert not database_path.exists()


def test_production_session_cookie_is_always_secure(tmp_path):
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{tmp_path / 'secure-cookie.db'}"
    environment["SESSION_SECRET_KEY"] = secrets.token_urlsafe(32)
    environment["APP_ENV"] = "production"
    environment["SESSION_COOKIE_SECURE"] = "false"
    checked = subprocess.run(
        [
            sys.executable,
            "-c",
            "from app.main import app; "
            "session = next(m for m in app.user_middleware "
            "if m.cls.__name__ == 'SessionMiddleware'); "
            "assert session.kwargs['https_only'] is True",
        ],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert checked.returncode == 0, checked.stderr


def test_concurrent_initialization_of_new_database(tmp_path):
    database_path = tmp_path / "concurrent.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"

    def initialize():
        return subprocess.run(
            [sys.executable, "-m", "app.initialize"],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(lambda _: initialize(), range(3)))

    assert [result.returncode for result in results] == [0, 0, 0], [
        result.stderr for result in results
    ]

    from sqlalchemy import create_engine

    test_engine = create_engine(f"sqlite:///{database_path}")
    try:
        tables = inspect(test_engine).get_table_names()
        assert {"players", "challenge_attempts", "rate_limit_buckets"} <= set(tables)
    finally:
        test_engine.dispose()


def test_legacy_database_upgrade_and_non_destructive_rollback(tmp_path):
    database_path = tmp_path / "legacy.db"
    environment = os.environ.copy()
    environment["DATABASE_URL"] = f"sqlite:///{database_path}"
    create_legacy_schema = """
from sqlalchemy import create_engine, insert
from app.models import Player, ChallengeAttempt
engine = create_engine(__import__('os').environ['DATABASE_URL'])
Player.__table__.create(engine)
ChallengeAttempt.__table__.create(engine)
with engine.begin() as connection:
    connection.execute(insert(Player).values(
        full_name='Legacy User',
        email='legacy@example.test',
        country='Ghana',
        alias='legacy-player',
        password='legacy-hash',
        royal_id='DR-GHA-2026-000010',
    ))
engine.dispose()
"""
    created = subprocess.run(
        [sys.executable, "-c", create_legacy_schema],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    assert created.returncode == 0, created.stderr

    for operation in (
        ("upgrade", "head"),
        ("downgrade", "base"),
        ("upgrade", "head"),
    ):
        migrated = subprocess.run(
            [sys.executable, "-m", "alembic", operation[0], operation[1]],
            env=environment,
            check=False,
            capture_output=True,
            text=True,
        )
        assert migrated.returncode == 0, migrated.stderr

    from sqlalchemy import create_engine, text

    test_engine = create_engine(f"sqlite:///{database_path}")
    try:
        with test_engine.connect() as connection:
            assert connection.scalar(
                text("SELECT email FROM players WHERE id = 1")
            ) == "legacy@example.test"
            assert "rate_limit_buckets" in inspect(test_engine).get_table_names()
    finally:
        test_engine.dispose()
