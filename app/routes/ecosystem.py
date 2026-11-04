import os
from datetime import datetime, timezone

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.database import SessionLocal
from app.ecosystem import (
    CATALOG_SECTIONS, CATALOG_STATUSES, INITIAL_NEWS, NEWS_CATEGORIES,
    NEWS_CATEGORY_BY_SLUG, SECTIONS,
)
from app.models import CatalogItem, Enquiry, NewsPost, Player
from app.csrf import csrf_token, verify_csrf

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")
ENQUIRY_REDIRECTS = {
    "resort": "/ecosystem/resort?sent=1",
    "journey": "/ecosystem/journey?sent=1",
    "polo": "/ecosystem/polo?sent=1",
    "livestock": "/ecosystem/livestock?sent=1",
    "luxury": "/ecosystem/luxury?sent=1",
}
CATALOG_REDIRECTS = {
    "livestock": "/admin/catalog/livestock",
    "luxury": "/admin/catalog/luxury",
}


# ---------- helpers ----------

def _emails(var):
    return {e.strip().lower() for e in os.environ.get(var, "").split(",") if e.strip()}


def is_admin(player):
    return bool(player) and player.email.lower() in _emails("DAMBA_ADMIN_EMAILS")


def can_manage_catalog(player, section):
    if not player:
        return False
    if is_admin(player):
        return True
    return (section == "livestock"
            and player.email.lower() in _emails("DAMBA_LIVESTOCK_ADMIN_EMAILS"))


def current_player(request, db):
    pid = request.session.get("player_id")
    return db.query(Player).filter(Player.id == pid).first() if pid else None


def check_csrf(request, token):
    verify_csrf(request, token)


class LoginRequired(Exception):
    pass


def require_player(request, db):
    player = current_player(request, db)
    if not player:
        raise LoginRequired()
    return player


def require_admin(request, db):
    player = require_player(request, db)
    if not is_admin(player):
        raise HTTPException(status_code=403, detail="Administrator access required.")
    return player


def render(request, name, **ctx):
    ctx["csrf"] = csrf_token(request)
    ctx["sections"] = SECTIONS
    return templates.TemplateResponse(request=request, name=name, context=ctx)


def seed_news(db):
    """Add the initial announcements only when no news exists yet."""
    if db.query(NewsPost).count() == 0:
        for title, category, body in INITIAL_NEWS:
            db.add(NewsPost(title=title, category=category, body=body, published=True))
        db.commit()


def published_news(db):
    return (db.query(NewsPost).filter(NewsPost.published.is_(True))
            .order_by(NewsPost.created_at.desc(), NewsPost.id.desc()).all())


def clean(value, limit):
    return (value or "").strip()[:limit]


# ---------- public pages ----------

@router.get("/ecosystem", response_class=HTMLResponse)
def hub(request: Request):
    db = SessionLocal()
    try:
        return render(request, "ecosystem_hub.html", player=current_player(request, db))
    finally:
        db.close()


@router.get("/ecosystem/{slug}", response_class=HTMLResponse)
def section_page(request: Request, slug: str, sent: int = 0):
    if slug not in SECTIONS:
        raise HTTPException(status_code=404, detail="Section not found.")
    db = SessionLocal()
    try:
        items = []
        if slug in CATALOG_SECTIONS:
            items = (db.query(CatalogItem)
                     .filter(CatalogItem.section == slug, CatalogItem.published.is_(True))
                     .order_by(CatalogItem.name).all())
        player = current_player(request, db)
        return render(request, "section.html", slug=slug, s=SECTIONS[slug], items=items,
                      statuses=CATALOG_STATUSES, player=player, sent=bool(sent),
                      can_manage=can_manage_catalog(player, slug),
                      news=[n for n in published_news(db) if n.category == NEWS_CATEGORY_BY_SLUG.get(slug)][:3])
    finally:
        db.close()


@router.post("/ecosystem/{slug}/enquiry")
def submit_enquiry(request: Request, slug: str, subject: str = Form(""),
                   message: str = Form(...), contact: str = Form(""),
                   item_id: str = Form(""), csrf: str = Form("")):
    if slug not in SECTIONS or not SECTIONS[slug].get("enquiry"):
        raise HTTPException(status_code=404, detail="Section not found.")
    db = SessionLocal()
    try:
        player = require_player(request, db)
        check_csrf(request, csrf)
        message = clean(message, 2000)
        if not message:
            raise HTTPException(status_code=422, detail="Message is required.")
        item = None
        if item_id.isdigit():
            item = db.query(CatalogItem).filter(
                CatalogItem.id == int(item_id), CatalogItem.section == slug).first()
        db.add(Enquiry(player_id=player.id, section=slug, subject=clean(subject, 200),
                       message=message, contact=clean(contact, 200),
                       item_id=item.id if item else None))
        db.commit()
        return RedirectResponse(ENQUIRY_REDIRECTS[slug], status_code=303)
    finally:
        db.close()


# ---------- admin: news ----------

@router.get("/admin/news", response_class=HTMLResponse)
def admin_news(request: Request, edit: int = 0):
    db = SessionLocal()
    try:
        player = require_admin(request, db)
        posts = db.query(NewsPost).order_by(NewsPost.created_at.desc()).all()
        editing = db.query(NewsPost).filter(NewsPost.id == edit).first() if edit else None
        return render(request, "admin_news.html", player=player, posts=posts,
                      editing=editing, categories=NEWS_CATEGORIES)
    finally:
        db.close()


@router.post("/admin/news")
def admin_news_save(request: Request, title: str = Form(...), body: str = Form(...),
                    category: str = Form("General"), published: str = Form(""),
                    post_id: str = Form(""), csrf: str = Form("")):
    db = SessionLocal()
    try:
        require_admin(request, db)
        check_csrf(request, csrf)
        title, body = clean(title, 200), clean(body, 5000)
        if not title or not body:
            raise HTTPException(status_code=422, detail="Title and body are required.")
        if category not in NEWS_CATEGORIES:
            category = "General"
        if post_id.isdigit():
            post = db.query(NewsPost).filter(NewsPost.id == int(post_id)).first()
            if not post:
                raise HTTPException(status_code=404, detail="Post not found.")
            post.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            post = NewsPost()
            db.add(post)
        post.title, post.body, post.category = title, body, category
        post.published = bool(published)
        db.commit()
        return RedirectResponse("/admin/news", status_code=303)
    finally:
        db.close()


@router.post("/admin/news/{post_id}/toggle")
def admin_news_toggle(request: Request, post_id: int, csrf: str = Form("")):
    db = SessionLocal()
    try:
        require_admin(request, db)
        check_csrf(request, csrf)
        post = db.query(NewsPost).filter(NewsPost.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found.")
        post.published = not post.published
        post.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        db.commit()
        return RedirectResponse("/admin/news", status_code=303)
    finally:
        db.close()


# ---------- admin: catalogue (livestock / luxury) ----------

def _catalog_section(section):
    if section not in CATALOG_SECTIONS:
        raise HTTPException(status_code=404, detail="Section not found.")


@router.get("/admin/catalog/{section}", response_class=HTMLResponse)
def admin_catalog(request: Request, section: str, edit: int = 0):
    _catalog_section(section)
    db = SessionLocal()
    try:
        player = require_player(request, db)
        if not can_manage_catalog(player, section):
            raise HTTPException(status_code=403, detail="Not authorized.")
        items = (db.query(CatalogItem).filter(CatalogItem.section == section)
                 .order_by(CatalogItem.name).all())
        editing = (db.query(CatalogItem).filter(CatalogItem.id == edit,
                   CatalogItem.section == section).first() if edit else None)
        return render(request, "admin_catalog.html", player=player, section=section,
                      s=SECTIONS[section], items=items, editing=editing,
                      statuses=CATALOG_STATUSES)
    finally:
        db.close()


@router.post("/admin/catalog/{section}")
def admin_catalog_save(request: Request, section: str, name: str = Form(...),
                       category: str = Form(""), description: str = Form(""),
                       price_note: str = Form(""), status: str = Form("available"),
                       published: str = Form(""), item_id: str = Form(""),
                       csrf: str = Form("")):
    _catalog_section(section)
    db = SessionLocal()
    try:
        player = require_player(request, db)
        if not can_manage_catalog(player, section):
            raise HTTPException(status_code=403, detail="Not authorized.")
        check_csrf(request, csrf)
        name = clean(name, 200)
        if not name:
            raise HTTPException(status_code=422, detail="Name is required.")
        if status not in CATALOG_STATUSES:
            status = "available"
        if item_id.isdigit():
            item = db.query(CatalogItem).filter(
                CatalogItem.id == int(item_id), CatalogItem.section == section).first()
            if not item:
                raise HTTPException(status_code=404, detail="Item not found.")
            item.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        else:
            item = CatalogItem(section=section)
            db.add(item)
        item.name, item.category = name, clean(category, 100)
        item.description, item.price_note = clean(description, 3000), clean(price_note, 200)
        item.status, item.published = status, bool(published)
        db.commit()
        return RedirectResponse(CATALOG_REDIRECTS[section], status_code=303)
    finally:
        db.close()


# ---------- admin: enquiries ----------

@router.get("/admin/enquiries", response_class=HTMLResponse)
def admin_enquiries(request: Request):
    db = SessionLocal()
    try:
        player = require_player(request, db)
        rows = (db.query(Enquiry, Player).join(Player, Player.id == Enquiry.player_id)
                .order_by(Enquiry.created_at.desc()).all())
        if not (is_admin(player) or can_manage_catalog(player, "livestock")):
            raise HTTPException(status_code=403, detail="Not authorized.")
        rows = [r for r in rows if can_manage_catalog(player, r[0].section)]
        return render(request, "admin_enquiries.html", player=player, rows=rows)
    finally:
        db.close()
