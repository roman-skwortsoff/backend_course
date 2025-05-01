"""fix rooms description

Revision ID: c0c1905d4564
Revises: f12f8b52ac10
Create Date: 2025-05-01 21:29:25.428010

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c0c1905d4564"
down_revision: Union[str, None] = "f12f8b52ac10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "rooms",
        "description",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "rooms",
        "description",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=True,
    )
