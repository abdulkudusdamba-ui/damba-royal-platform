from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0001_safe_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    existing_tables = set(inspect(op.get_bind()).get_table_names())

    if "players" not in existing_tables:
        op.create_table(
            "players",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("royal_id", sa.String(), nullable=True),
            sa.Column("full_name", sa.String(), nullable=False),
            sa.Column("email", sa.String(), nullable=False),
            sa.Column("country", sa.String(), nullable=False),
            sa.Column("alias", sa.String(), nullable=False),
            sa.Column("password", sa.String(), nullable=False),
            sa.Column("xp", sa.Integer(), nullable=True),
            sa.Column("royal_tokens", sa.Integer(), nullable=True),
            sa.Column("level", sa.String(), nullable=True),
            sa.Column("badge", sa.String(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("alias"),
            sa.UniqueConstraint("email"),
            sa.UniqueConstraint("royal_id"),
        )
        op.create_index("ix_players_id", "players", ["id"], unique=False)
        op.create_index("ix_players_royal_id", "players", ["royal_id"], unique=True)

    if "challenge_attempts" not in existing_tables:
        op.create_table(
            "challenge_attempts",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("player_id", sa.Integer(), nullable=False),
            sa.Column("challenge_id", sa.String(), nullable=False),
            sa.Column("answer", sa.String(), nullable=False),
            sa.Column("correct", sa.Integer(), nullable=False),
            sa.Column("score", sa.Integer(), nullable=False),
            sa.Column("xp_awarded", sa.Integer(), nullable=False),
            sa.Column("tokens_awarded", sa.Integer(), nullable=False),
            sa.Column("completed_at", sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "player_id",
                "challenge_id",
                name="uq_player_challenge",
            ),
        )
        op.create_index(
            "ix_challenge_attempts_id",
            "challenge_attempts",
            ["id"],
            unique=False,
        )
        op.create_index(
            "ix_challenge_attempts_player_id",
            "challenge_attempts",
            ["player_id"],
            unique=False,
        )
        op.create_index(
            "ix_challenge_attempts_challenge_id",
            "challenge_attempts",
            ["challenge_id"],
            unique=False,
        )

    if "rate_limit_buckets" not in existing_tables:
        op.create_table(
            "rate_limit_buckets",
            sa.Column("bucket_key", sa.String(length=64), nullable=False),
            sa.Column("window_started", sa.DateTime(), nullable=False),
            sa.Column("request_count", sa.Integer(), nullable=False),
            sa.Column("expires_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("bucket_key"),
        )
        op.create_index(
            "ix_rate_limit_buckets_expires_at",
            "rate_limit_buckets",
            ["expires_at"],
            unique=False,
        )


def downgrade():
    pass
