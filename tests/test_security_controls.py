from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import hashlib

from fastapi.testclient import TestClient
from sqlalchemy import select, update

from app.cleanup_rate_limits import cleanup_expired_buckets
from app.database import SessionLocal
from app.main import app
from app.models import ChallengeAttempt, Player, RateLimitBucket
from app.challenges import get_challenge
from app.rate_limiting import _consume
from app.security import hash_password


def client(ip="198.51.100.10"):
    return TestClient(app, client=(ip, 12345))


def same_origin():
    return {"Origin": "http://testserver"}


def test_login_uses_generic_credentials_error_and_rate_limit(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_LOGIN_MAX", "2")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "60")
    with SessionLocal() as session:
        player = Player(
            full_name="Known User",
            email="known@example.test",
            country="Ghana",
            alias="known-player",
            royal_id="DR-GHA-2026-000100",
        )
        player.password = hash_password("actual-password")
        session.add(player)
        session.commit()

    test_client = client("198.51.100.11")

    first = test_client.post(
        "/auth/login",
        data={"email": "absent@example.test", "password": "not-the-password"},
        headers=same_origin(),
    )
    second = test_client.post(
        "/auth/login",
        data={"email": "known@example.test", "password": "not-the-password"},
        headers=same_origin(),
    )
    limited = test_client.post(
        "/auth/login",
        data={"email": "absent@example.test", "password": "not-the-password"},
        headers=same_origin(),
    )

    assert first.status_code == second.status_code == 401
    assert first.json() == second.json()
    assert limited.status_code == 429
    assert int(limited.headers["Retry-After"]) > 0


def test_origin_guard_rejects_cross_site_post_and_allows_same_origin():
    test_client = client("198.51.100.12")
    rejected = test_client.post(
        "/auth/login",
        data={"email": "someone@example.test", "password": "x"},
        headers={"Origin": "https://attacker.example"},
    )
    accepted = test_client.post(
        "/auth/login",
        data={"email": "someone@example.test", "password": "x"},
        headers=same_origin(),
    )

    assert rejected.status_code == 403
    assert accepted.status_code == 401


def test_unauthenticated_challenge_api_returns_401():
    response = client("198.51.100.15").get("/api/challenges/next")
    assert response.status_code == 401


def test_registration_collision_does_not_disclose_existing_account():
    test_client = client("198.51.100.13")
    form = {
        "full_name": "First User",
        "email": "same@example.test",
        "country": "Ghana",
        "alias": "unique-alias",
        "password": "long-enough-test-password",
    }
    first = test_client.post(
        "/auth/register",
        data=form,
        headers=same_origin(),
        follow_redirects=False,
    )
    duplicate = test_client.post(
        "/auth/register",
        data={**form, "alias": "another-alias"},
        headers=same_origin(),
        follow_redirects=False,
    )

    assert first.status_code == duplicate.status_code == 303
    assert first.headers["location"] == duplicate.headers["location"] == "/login"


def test_concurrent_challenge_submissions_award_rewards_once():
    with SessionLocal() as session:
        player = Player(
            full_name="Concurrent User",
            email="concurrent@example.test",
            country="Ghana",
            alias="concurrent-player",
            royal_id="DR-CAN-2026-990001",
            xp=0,
            royal_tokens=0,
        )
        player.password = hash_password("long-enough-test-password")
        session.add(player)
        session.commit()
        player_id = player.id

    login_client = client("198.51.100.16")
    login_response = login_client.post(
        "/auth/login",
        data={
            "email": "concurrent@example.test",
            "password": "long-enough-test-password",
        },
        headers=same_origin(),
        follow_redirects=False,
    )
    assert login_response.status_code == 303

    cookies = dict(login_client.cookies)
    challenge = get_challenge("mission-001")
    answer = str(challenge["correct_answer"])
    payload = {"answer": answer, "time_left": "30"}

    def submit():
        test_client = client("198.51.100.16")
        test_client.cookies.update(cookies)
        return test_client.post(
            "/api/challenges/mission-001/complete",
            data=payload,
            headers=same_origin(),
        )

    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: submit(), range(2)))

    assert all(response.status_code == 200 for response in responses)
    assert sum(response.json().get("success") is True for response in responses) == 1
    assert sum(response.json().get("already_completed") is True for response in responses) == 1

    with SessionLocal() as session:
        attempts = (
            session.query(ChallengeAttempt)
            .filter(
                ChallengeAttempt.player_id == player_id,
                ChallengeAttempt.challenge_id == "mission-001",
            )
            .count()
        )
        stored_player = session.get(Player, player_id)
        assert attempts == 1
        assert stored_player.xp == challenge["xp_correct"]


def test_expired_rate_limit_window_allows_legitimate_retry(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_LOGIN_MAX", "1")
    monkeypatch.setenv("RATE_LIMIT_LOGIN_WINDOW_SECONDS", "60")
    first = client("198.51.100.14").post(
        "/auth/login",
        data={"email": "absent@example.test", "password": "x"},
        headers=same_origin(),
    )
    assert first.status_code == 401

    with SessionLocal() as session:
        row = session.scalar(
            select(RateLimitBucket).where(
                RateLimitBucket.bucket_key
                == hashlib.sha256(b"login:198.51.100.14").hexdigest()
            )
        )
        assert row is not None
        session.execute(
            update(RateLimitBucket)
            .where(RateLimitBucket.bucket_key == row.bucket_key)
            .values(
                window_started=datetime.now(timezone.utc).replace(tzinfo=None)
                - timedelta(seconds=120)
            )
        )
        session.commit()

    retry = client("198.51.100.14").post(
        "/auth/login",
        data={"email": "absent@example.test", "password": "x"},
        headers=same_origin(),
    )
    assert retry.status_code == 401


def test_concurrent_rate_limit_updates_are_atomic():
    key = "atomic-test-bucket"

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: _consume(key, 60)[0], range(16)))

    assert max(results) == 16
    assert min(results) >= 1


def test_rate_limit_maintenance_removes_only_expired_buckets():
    expired_key = "expired-bucket-test"
    active_key = "active-bucket-test"
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    with SessionLocal() as session:
        session.add_all(
            [
                RateLimitBucket(
                    bucket_key=expired_key,
                    window_started=now - timedelta(hours=2),
                    request_count=1,
                    expires_at=now - timedelta(hours=1),
                ),
                RateLimitBucket(
                    bucket_key=active_key,
                    window_started=now,
                    request_count=1,
                    expires_at=now + timedelta(hours=1),
                ),
            ]
        )
        session.commit()

    assert cleanup_expired_buckets() >= 1
    with SessionLocal() as session:
        assert session.get(RateLimitBucket, expired_key) is None
        assert session.get(RateLimitBucket, active_key) is not None
