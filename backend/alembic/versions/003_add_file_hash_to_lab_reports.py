"""Add file_hash to lab_reports for deduplication

Revision ID: 003
Revises: 002
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('lab_reports', sa.Column('file_hash', sa.String(64), nullable=True))
    op.create_index('ix_lab_reports_file_hash', 'lab_reports', ['file_hash'])


def downgrade() -> None:
    op.drop_index('ix_lab_reports_file_hash', table_name='lab_reports')
    op.drop_column('lab_reports', 'file_hash')
