"""add unique email

Revision ID: f12f8b52ac10
Revises: d2ac5fede729
Create Date: 2025-04-29 11:10:48.166814

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "f12f8b52ac10"
down_revision: Union[str, None] = "d2ac5fede729"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS citext"
    )  # вручную включаем расширение CITEXT для email
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(length=100),
        type_=postgresql.CITEXT(length=100),
        existing_nullable=False,
    )
    op.create_unique_constraint(None, "users", ["email"])


def downgrade() -> None:
    op.drop_constraint(None, "users", type_="unique")
    op.alter_column(
        "users",
        "email",
        existing_type=postgresql.CITEXT(length=100),
        type_=sa.VARCHAR(length=100),
        existing_nullable=False,
    )
