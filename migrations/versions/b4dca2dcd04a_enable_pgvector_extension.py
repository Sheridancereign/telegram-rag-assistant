"""enable pgvector extension

Revision ID: b4dca2dcd04a
Revises: 
Create Date: 2026-08-08 12:38:18.168515

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4dca2dcd04a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")



def downgrade() -> None:
     op.execute("DROP EXTENSION IF EXISTS vector")
