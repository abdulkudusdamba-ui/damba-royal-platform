# Damba Royal

Damba Royal is a Northern Ghana heritage-inspired platform for Season Zero training and online Royal Labyrinth competition. The future physical arena is an ambition, not an existing venue.

## Run locally

```bash
python -m pip install -r requirements.txt
export SESSION_SECRET="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
uvicorn app.main:app --reload
```

The application uses `sqlite:///./damba_royal.db` by default. Set `DATABASE_URL` to select another SQLAlchemy database URL. Existing database files are retained; startup creates missing tables and does not reset player data.

## Online competition

Sign in as two separate player accounts. The first player creates a room and shares its six-character code; the second player joins with that code. Both mark themselves ready, then the host starts the competition. Both browsers enter the same server-selected, timed round and see finalized scores after both answers are submitted or the shared deadline expires.

## Checks

```bash
python -m unittest discover -s tests
```
