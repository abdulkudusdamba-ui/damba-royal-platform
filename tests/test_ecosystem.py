import os
import re
import tempfile
from pathlib import Path

TEST_DATABASE = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(TEST_DATABASE.name) / 'test.db'}"
os.environ["SESSION_SECRET_KEY"] = "test-only-session-secret-for-isolated-tests"
os.environ["DAMBA_ADMIN_EMAILS"] = "admin@example.com"
os.environ["DAMBA_LIVESTOCK_ADMIN_EMAILS"] = "stock@example.com"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ecosystem import SECTIONS
from app.challenges import get_challenge
from app.database import SessionLocal
from app.models import Player, NewsPost, CatalogItem, Enquiry


def register(client, email, alias):
    token = csrf(client, "/register")
    client.post("/auth/register", data={
        "full_name": "T " + alias, "email": email, "country": "Ghana",
        "alias": alias, "password": "pass1234", "csrf": token})
    client.post("/auth/login", data={
        "email": email, "password": "pass1234", "csrf": csrf(client, "/login")})


def csrf(client, path="/ecosystem/resort"):
    return re.search(r'name="csrf" value="([^"]+)"', client.get(path).text).group(1)


@pytest.fixture(scope="module")
def cleanup():
    yield
    db = SessionLocal()
    emails = ["admin@example.com", "stock@example.com", "user@example.com"]
    ids = [p.id for p in db.query(Player).filter(Player.email.in_(emails))]
    db.query(Enquiry).filter(Enquiry.player_id.in_(ids)).delete(synchronize_session=False)
    db.query(CatalogItem).filter(CatalogItem.name.like("TEST%")).delete(synchronize_session=False)
    db.query(NewsPost).filter(NewsPost.title.like("TEST%")).delete(synchronize_session=False)
    db.query(Player).filter(Player.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    db.close()


def test_all_pages_and_links(cleanup):
    c = TestClient(app)
    assert "dambaroyal@gmail.com" in c.get("/").text
    assert c.get("/ecosystem").status_code == 200
    for slug in SECTIONS:
        r = c.get(f"/ecosystem/{slug}")
        assert r.status_code == 200
        assert "Current availability" in r.text
    assert c.get("/ecosystem/nope").status_code == 404
    register(c, "user@example.com", "testuser1")
    dash = c.get("/dashboard")
    assert dash.status_code == 200
    assert "Royal News" in dash.text and "under development" in dash.text
    for href in set(re.findall(r'href="(/[^"#]*)"', dash.text)):
        if href == "/auth/logout":
            continue
        assert c.get(href, follow_redirects=False).status_code in (200, 303, 403), href
    assert c.get("/challenge").status_code == 200


def test_auth_csrf_and_post_logout():
    c = TestClient(app)
    token = csrf(c, "/register")
    account = {
        "full_name": "CSRF Test",
        "email": "csrf@example.com",
        "country": "Ghana",
        "alias": "csrftest",
        "password": "pass1234",
    }
    assert c.post("/auth/register", data=account).status_code == 403
    assert c.post(
        "/auth/register",
        data={**account, "csrf": token},
        follow_redirects=False,
    ).status_code == 303
    login_token = csrf(c, "/login")
    assert c.post(
        "/auth/login",
        data={"email": account["email"], "password": account["password"]},
    ).status_code == 403
    assert c.post(
        "/auth/login",
        data={"email": account["email"], "password": account["password"], "csrf": login_token},
        follow_redirects=False,
    ).status_code == 303
    assert c.get("/auth/logout").status_code == 405
    assert c.post("/auth/logout").status_code == 403
    assert c.post(
        "/auth/logout",
        data={"csrf": csrf(c, "/dashboard")},
        follow_redirects=False,
    ).status_code == 303
    assert c.get("/api/player").json() == {"error": "Not authenticated"}


def test_training_challenge_requires_csrf_and_preserves_progress():
    c = TestClient(app)
    register(c, "challenge@example.com", "testchallenge")
    challenge = c.get("/api/challenges/next").json()["challenge"]
    answer = get_challenge(challenge["id"])["correct_answer"]
    form = {"answer": answer, "time_left": "30"}
    assert c.post(
        f"/api/challenges/{challenge['id']}/complete",
        data=form,
    ).status_code == 403
    result = c.post(
        f"/api/challenges/{challenge['id']}/complete",
        data={**form, "csrf": csrf(c, "/dashboard")},
    )
    assert result.status_code == 200
    assert result.json()["success"] is True
    duplicate = c.post(
        f"/api/challenges/{challenge['id']}/complete",
        data={**form, "csrf": csrf(c, "/dashboard")},
    )
    assert duplicate.json()["already_completed"] is True


def test_enquiry_requires_login_and_csrf():
    anon = TestClient(app)
    r = anon.post("/ecosystem/resort/enquiry", data={"message": "x"}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/login"
    c = TestClient(app)
    register(c, "user@example.com", "testuser1")
    assert c.post("/ecosystem/resort/enquiry", data={"message": "x", "csrf": "bad"}).status_code == 403
    ok = c.post("/ecosystem/resort/enquiry", data={"message": "hi", "csrf": csrf(c)},
                follow_redirects=False)
    assert ok.status_code == 303


def test_admin_protection():
    anon = TestClient(app)
    assert anon.get("/admin/news", follow_redirects=False).status_code == 303
    user = TestClient(app)
    register(user, "user@example.com", "testuser1")
    for path in ("/admin/news", "/admin/catalog/livestock", "/admin/catalog/luxury", "/admin/enquiries"):
        assert user.get(path).status_code == 403
    assert user.post("/admin/news", data={"title": "TEST", "body": "b", "csrf": csrf(user)}).status_code == 403


def test_news_admin_flow():
    c = TestClient(app)
    register(c, "admin@example.com", "testadmin1")
    assert c.get("/admin/news").status_code == 200
    r = c.post("/admin/news", data={"title": "TEST post", "body": "hello", "category": "Resort",
                                    "published": "1", "csrf": csrf(c, "/admin/news")})
    assert r.status_code == 200
    assert "TEST post" in c.get("/dashboard").text
    post = SessionLocal().query(NewsPost).filter(NewsPost.title == "TEST post").one()
    c.post(f"/admin/news/{post.id}/toggle", data={"csrf": csrf(c, "/admin/news")})
    assert "TEST post" not in c.get("/dashboard").text
    assert c.post(f"/admin/news/{post.id}/toggle", data={"csrf": "bad"}).status_code == 403


def test_livestock_admin_scope():
    c = TestClient(app)
    register(c, "stock@example.com", "teststock1")
    assert c.get("/admin/catalog/livestock").status_code == 200
    assert c.get("/admin/catalog/luxury").status_code == 403
    assert c.get("/admin/news").status_code == 403
    r = c.post("/admin/catalog/livestock", data={
        "name": "TEST cow", "status": "available", "published": "1",
        "csrf": csrf(c, "/admin/catalog/livestock")})
    assert r.status_code == 200
    page = c.get("/ecosystem/livestock").text
    assert "TEST cow" in page and "Available" in page
