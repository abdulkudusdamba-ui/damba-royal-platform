# Damba Royal

Damba Royal combines online Royal Labyrinth training, two-player live competitions, and heritage ecosystem pages. The physical resort and equestrian park are planned, not operating. Bookings, online payments, wallet transfers, and visa services are not available; related requests are enquiries only.

Official contact: [dambaroyal@gmail.com](mailto:dambaroyal@gmail.com).

## Run locally

```bash
python -m pip install -r requirements.txt
export SESSION_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
uvicorn app.main:app --reload
```

The app uses `sqlite:///./damba_royal.db` by default. Set `DATABASE_URL` to choose another SQLAlchemy database. Existing database files and player records are retained; startup creates missing tables but does not alter existing tables. Schema changes to existing tables require a reviewed migration.

Set `APP_ENV=production` and provide a stable `SESSION_SECRET_KEY` through the deployment secret manager in production. Production cookies are HTTPS-only. Set `DAMBA_ADMIN_EMAILS` and, if needed, `DAMBA_LIVESTOCK_ADMIN_EMAILS` to comma-separated authorized account emails.

## Online competition

Sign in with two separate accounts. The first player creates a room and shares its six-character code; the second joins. Both mark ready before the host can start. The server selects the shared challenge, enforces the deadline, accepts one answer per player, and reveals results only after both answers or timeout.

## Tests

```bash
python -m pytest -q
```

The test suite configures temporary SQLite databases; do not point tests at a database containing user data.
