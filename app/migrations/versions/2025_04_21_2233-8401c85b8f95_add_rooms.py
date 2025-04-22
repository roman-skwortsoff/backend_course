"""add rooms

Revision ID: 8401c85b8f95
Revises: 5124f6fc5d59
Create Date: 2025-04-21 22:33:01.789710

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8401c85b8f95"
down_revision: Union[str, None] = "5124f6fc5d59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("hotel_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.Integer(), nullable=True),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["hotel_id"],
            ["hotels.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("rooms")
