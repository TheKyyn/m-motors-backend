"""ensure_documents_list

Revision ID: 5fbfe07c4d03
Revises: 573418e2bcd8
Create Date: 2025-02-18 03:19:08.987971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '5fbfe07c4d03'
down_revision: Union[str, None] = '573418e2bcd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Mettre à jour les documents null ou vides en listes vides
    op.execute("""
        UPDATE dossiers 
        SET documents = '[]'::jsonb 
        WHERE documents IS NULL OR documents = '{}'::jsonb
    """)


def downgrade() -> None:
    # Pas de downgrade nécessaire car nous ne voulons pas revenir à des documents invalides
    pass
