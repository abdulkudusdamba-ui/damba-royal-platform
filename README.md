# damba-royal-platform
Official source code for the Damba Royal Platform — a global luxury heritage, tourism, and Royal Labyrinth ecosystem connecting players worldwide.

## Configuration

- `SESSION_SECRET_KEY` – required in production (`APP_ENV=production`); the app refuses to start without it. Generate one with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
- `APP_ENV` – set to `production` on deployment. In development, if the secret is unset, a random ephemeral key is used (sessions reset on restart).

Local: `export SESSION_SECRET_KEY=...` then `uvicorn app.main:app --reload`. Deployment: set both variables in your host's secret manager.
