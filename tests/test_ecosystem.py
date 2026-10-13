import os
import re

os.environ["DAMBA_ADMIN_EMAILS"] = "admin@example.com"
os.environ["DAMBA_LIVESTOCK_ADMIN_EMAILS"] = "stock@example.com"

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ecosystem import SECTIONS
from app.database import SessionLocal
from app.models import Player, NewsPost, CatalogItem, Enquiry


def register(client, email, alias):
    client.post("/auth/register", data={
        "full_name": "T " + alias, "email": email, "country": "Ghana",
        "alias": alias, "password": "pass1234"})
    client.post("/auth/login", data={"email": email, "password": "pass1234"})


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
