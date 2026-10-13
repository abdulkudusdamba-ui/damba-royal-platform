# Damba Royal Platform

Official source code for the Damba Royal Platform.

## Local setup and tests

Use Python 3.12 or newer. Install the application and test dependencies:

```sh
python -m pip install -r requirements-dev.txt
export DATABASE_URL="sqlite:///./damba_royal.db"
export SESSION_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m app.initialize
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run the automated tests with `python -m pytest -q`. Tests create temporary
databases and do not use `damba_royal.db`.

## Database initialization, migrations, and recovery

Application import and worker startup do not create or alter tables, and do not
seed news or other content. Run `python -m app.initialize` once before starting
workers. It applies Alembic revisions while holding a database-wide PostgreSQL
advisory lock or a SQLite exclusive lock. SQLite and PostgreSQL are the supported
databases for initialization and shared rate-limit storage. Configure a
PostgreSQL URL as `postgresql+psycopg://...` and keep credentials in the
deployment environment, not source control.

The initial baseline creates only missing tables. It adopts an existing
`players`/`challenge_attempts` schema without dropping tables or rows and adds
the rate-limit table. Its downgrade intentionally leaves all tables and data in
place. For rollback, take the service offline and restore a verified
pre-migration backup to a compatible database; do not treat Alembic downgrade
as a data rollback.

Before each migration, create and verify a recoverable backup. For PostgreSQL,
use `pg_dump` and test restoring it into an isolated database. For SQLite, stop
all writers and use SQLite's online backup mechanism (or copy the database
while the application is stopped); verify the copy can be opened and restored
before proceeding. Never test migrations against a production database.

## Production security and limits

Set `APP_ENV=production`, a randomly generated `SESSION_SECRET_KEY` of at least
32 bytes, and a shared PostgreSQL `DATABASE_URL`. Production cookies always use
the Secure flag; sessions are HttpOnly, SameSite=Lax, and expire after one hour
by default (`SESSION_MAX_AGE_SECONDS` is configurable). Rotating the signing
secret invalidates existing sessions. Unsafe requests require a same-host
Origin or Referer; reverse proxies must preserve the original host/scheme and
be explicitly trusted by the ASGI server.

Rate limits are stored in the shared application database and default to:

| Action | Requests | Window |
| --- | ---: | ---: |
| Login | 5 | 60 seconds |
| Registration | 3 | 3600 seconds |
| Enquiry | 5 | 3600 seconds |
| Live-room creation | 5 | 3600 seconds |
| Live-room join | 20 | 60 seconds |
| Challenge submission | 30 | 60 seconds |

Override each action with `RATE_LIMIT_<ACTION>_MAX` and
`RATE_LIMIT_<ACTION>_WINDOW_SECONDS` (for example,
`RATE_LIMIT_LOGIN_MAX=5`). Rate limits are keyed by the client IP address.
Schedule `python -m app.cleanup_rate_limits` using the same database settings
to remove expired rate-limit counters; this job touches only the rate-limit
table.
Behind a reverse proxy, configure Uvicorn's trusted forwarded-IP handling with
only the actual proxy addresses; never trust arbitrary forwarded headers.

This checkout has no enquiry or live-room routes/models, room lifecycle,
cleanup/audit behavior, admin interface, or news seeding. The enquiry and room
limits are configured for future matching routes but currently have no endpoint
to protect. This implementation therefore does not establish production
readiness for those features.
