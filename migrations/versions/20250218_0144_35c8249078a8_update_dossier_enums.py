"""update dossier enums

Revision ID: 35c8249078a8
Revises: b8e464305a5c
Create Date: 2025-02-18 01:44:47.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '35c8249078a8'
down_revision = 'b8e464305a5c'
branch_labels = None
depends_on = None

def upgrade():
    # Supprimer les valeurs par défaut existantes
    op.execute("ALTER TABLE dossiers ALTER COLUMN type DROP DEFAULT")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status DROP DEFAULT")
    
    # Créer les types enum
    op.execute("CREATE TYPE dossiertype AS ENUM ('ACHAT', 'LOCATION')")
    op.execute("CREATE TYPE dossierstatus AS ENUM ('EN_ATTENTE', 'EN_COURS_DE_TRAITEMENT', 'DOCUMENTS_MANQUANTS', 'ACCEPTE', 'REFUSE', 'ANNULE')")
    
    # Convertir les valeurs existantes en majuscules
    op.execute("UPDATE dossiers SET type = UPPER(type), status = UPPER(REPLACE(status, ' ', '_'))")
    
    # Modifier les colonnes pour utiliser les types enum
    op.execute("ALTER TABLE dossiers ALTER COLUMN type TYPE dossiertype USING type::dossiertype")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status TYPE dossierstatus USING status::dossierstatus")
    
    # Ajouter les nouvelles valeurs par défaut
    op.execute("ALTER TABLE dossiers ALTER COLUMN type SET DEFAULT 'ACHAT'::dossiertype")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status SET DEFAULT 'EN_ATTENTE'::dossierstatus")

def downgrade():
    # Supprimer les valeurs par défaut
    op.execute("ALTER TABLE dossiers ALTER COLUMN type DROP DEFAULT")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status DROP DEFAULT")
    
    # Convertir les colonnes en VARCHAR
    op.execute("ALTER TABLE dossiers ALTER COLUMN type TYPE VARCHAR USING type::VARCHAR")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    
    # Ajouter les anciennes valeurs par défaut
    op.execute("ALTER TABLE dossiers ALTER COLUMN type SET DEFAULT 'achat'")
    op.execute("ALTER TABLE dossiers ALTER COLUMN status SET DEFAULT 'en_attente'")
    
    # Supprimer les types enum
    op.execute("DROP TYPE dossierstatus")
    op.execute("DROP TYPE dossiertype")
