"""add roles to users

Revision ID: 1a26e209b256
Revises: 9ea12bfca96a
Create Date: 2026-07-15 09:34:01.734085

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "1a26e209b256"
down_revision: Union[str, Sequence[str], None] = "9ea12bfca96a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    role_enum = sa.Enum("admin", "user", name="role")
    role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        "users", sa.Column("roles", role_enum, nullable=False, server_default="user")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "roles")
    sa.Enum(name="role").drop(op.get_bind(), checkfirst=True)
