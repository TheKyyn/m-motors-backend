"""add_rag_chat_tables

Revision ID: 20240610001
Depends on: 20250218_1620_c8041a2c282f
Create Date: 2024-06-10 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '20240610001'
down_revision = '20250218_1620_c8041a2c282f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'rag_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('embedding_status', sa.Boolean(), server_default=sa.text('false'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rag_documents_id'), 'rag_documents', ['id'], unique=False)
    
    op.create_table(
        'rag_document_chunks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('metadata', JSONB, nullable=True),
        sa.Column('embedding', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['rag_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rag_document_chunks_id'), 'rag_document_chunks', ['id'], unique=False)
    
    op.create_table(
        'rag_chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('session_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_activity', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rag_chat_sessions_id'), 'rag_chat_sessions', ['id'], unique=False)
    op.create_index(op.f('ix_rag_chat_sessions_session_id'), 'rag_chat_sessions', ['session_id'], unique=True)
    
    op.create_table(
        'rag_chat_messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('metadata', JSONB, nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['rag_chat_sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rag_chat_messages_id'), 'rag_chat_messages', ['id'], unique=False)


def downgrade():
    op.drop_table('rag_chat_messages')
    op.drop_table('rag_chat_sessions')
    op.drop_table('rag_document_chunks')
    op.drop_table('rag_documents') 