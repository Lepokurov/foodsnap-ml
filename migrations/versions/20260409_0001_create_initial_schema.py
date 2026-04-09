"""create initial schema"""

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "20260409_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "food_reference",
        sa.Column("label", sa.String(length=120), nullable=False),
        sa.Column("estimated_calories", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("label"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_table(
        "meal_entries",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("user_id", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("image_url", sa.String(length=1024), nullable=False),
        sa.Column("image_storage", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("meal_timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recognized_label", sa.String(length=120), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("estimated_calories", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_meal_entries_meal_timestamp"), "meal_entries", ["meal_timestamp"], unique=False)
    op.create_index(op.f("ix_meal_entries_status"), "meal_entries", ["status"], unique=False)
    op.create_index(op.f("ix_meal_entries_user_id"), "meal_entries", ["user_id"], unique=False)
    op.create_table(
        "meal_predictions",
        sa.Column("meal_id", sa.String(length=32), nullable=False),
        sa.Column("raw_label", sa.String(length=120), nullable=False),
        sa.Column("normalized_label", sa.String(length=120), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["meal_id"], ["meal_entries.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("meal_id"),
    )
    op.create_index(
        op.f("ix_meal_predictions_normalized_label"),
        "meal_predictions",
        ["normalized_label"],
        unique=False,
    )

    food_reference_table = sa.table(
        "food_reference",
        sa.column("label", sa.String(length=120)),
        sa.column("estimated_calories", sa.Integer()),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        food_reference_table,
        [
            {"label": "burger", "estimated_calories": 550, "created_at": now, "updated_at": now},
            {"label": "pizza", "estimated_calories": 700, "created_at": now, "updated_at": now},
            {"label": "salad", "estimated_calories": 280, "created_at": now, "updated_at": now},
            {"label": "pasta", "estimated_calories": 640, "created_at": now, "updated_at": now},
            {"label": "sushi", "estimated_calories": 420, "created_at": now, "updated_at": now},
            {"label": "steak", "estimated_calories": 610, "created_at": now, "updated_at": now},
            {"label": "soup", "estimated_calories": 240, "created_at": now, "updated_at": now},
            {"label": "unknown", "estimated_calories": 450, "created_at": now, "updated_at": now},
        ],
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_meal_predictions_normalized_label"), table_name="meal_predictions")
    op.drop_table("meal_predictions")
    op.drop_index(op.f("ix_meal_entries_user_id"), table_name="meal_entries")
    op.drop_index(op.f("ix_meal_entries_status"), table_name="meal_entries")
    op.drop_index(op.f("ix_meal_entries_meal_timestamp"), table_name="meal_entries")
    op.drop_table("meal_entries")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    op.drop_table("food_reference")
