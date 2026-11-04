import os
from pathlib import Path
import secrets
import tempfile


os.environ.setdefault(
    "DATABASE_URL",
    f"sqlite:///{Path(tempfile.mkdtemp()) / 'damba-test.db'}",
)
os.environ.setdefault("SESSION_SECRET_KEY", secrets.token_urlsafe(32))

import pytest

from app.initialize import initialize_database


@pytest.fixture(scope="session", autouse=True)
def initialized_database():
    initialize_database()
