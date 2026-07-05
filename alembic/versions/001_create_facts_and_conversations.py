"""create facts and conversations tables

Revision ID: 001
Revises:
Create Date: 2026-07-05
"""


import sqlalchemy as sa

from alembic import op

revision: str = "001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "facts",
        sa.Column("fact_id", sa.String(32), primary_key=True),
        sa.Column("key", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("value", sa.Text, nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "conversations",
        sa.Column("entry_id", sa.String(32), primary_key=True),
        sa.Column("user_input", sa.Text, nullable=False),
        sa.Column("system_response", sa.Text, nullable=True),
        sa.Column("action_summary", sa.Text, nullable=True),
        sa.Column("decision_verdict", sa.String(50), nullable=True),
        sa.Column("decision_reason", sa.Text, nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("conversations")
    op.drop_table("facts")
