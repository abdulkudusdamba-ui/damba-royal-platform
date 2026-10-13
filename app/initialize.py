from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.database import DATABASE_URL, engine


MIGRATION_LOCK_ID = 0x44414D4241


def initialize_database():
    if engine.dialect.name not in {"sqlite", "postgresql"}:
        raise RuntimeError(
            "Safe initialization is supported only for SQLite and PostgreSQL."
        )

    config = Config(str(Path(__file__).resolve().parent.parent / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", DATABASE_URL.replace("%", "%%"))

    with engine.connect() as connection:
        if engine.dialect.name == "sqlite":
            connection.exec_driver_sql("BEGIN EXCLUSIVE")
        else:
            connection.execute(
                text("SELECT pg_advisory_lock(:lock_id)"),
                {"lock_id": MIGRATION_LOCK_ID},
            )
            connection.commit()

        try:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
            if connection.in_transaction():
                connection.commit()
        finally:
            if engine.dialect.name == "postgresql":
                connection.execute(
                    text("SELECT pg_advisory_unlock(:lock_id)"),
                    {"lock_id": MIGRATION_LOCK_ID},
                )
                connection.commit()


if __name__ == "__main__":
    initialize_database()
