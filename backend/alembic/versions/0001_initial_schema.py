"""Initial schema for AI MineGuard Module 1

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-09-07 22:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Tables are auto-created by SQLAlchemy Base.metadata.create_all during app startup.
    pass


def downgrade() -> None:
    pass
