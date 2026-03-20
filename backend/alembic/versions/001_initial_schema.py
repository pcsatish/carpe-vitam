"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'])

    # Create families table
    op.create_table(
        'families',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_by', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create family_members table
    op.create_table(
        'family_members',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('family_id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=True),
        sa.Column('display_name', sa.String(255), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('sex', sa.String(20), nullable=True),
        sa.Column('role', sa.Enum('admin', 'member', 'viewer', name='familymemberrole'), nullable=False, server_default='member'),
        sa.Column('joined_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_id'], ['families.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_family_members_family_id'), 'family_members', ['family_id'])

    # Create analyte_catalog table
    op.create_table(
        'analyte_catalog',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('canonical_name', sa.String(255), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('canonical_unit', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('related_analyte_ids', sa.ARRAY(sa.String(36)), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canonical_name'),
    )
    op.create_index(op.f('ix_analyte_catalog_canonical_name'), 'analyte_catalog', ['canonical_name'])
    op.create_index(op.f('ix_analyte_catalog_category'), 'analyte_catalog', ['category'])
    op.create_index(op.f('ix_analyte_catalog_is_active'), 'analyte_catalog', ['is_active'])

    # Create analyte_aliases table
    op.create_table(
        'analyte_aliases',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('analyte_id', sa.String(36), nullable=False),
        sa.Column('raw_name', sa.String(255), nullable=False),
        sa.Column('lab_source', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['analyte_id'], ['analyte_catalog.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_analyte_aliases_analyte_id'), 'analyte_aliases', ['analyte_id'])
    op.create_index(op.f('ix_analyte_aliases_raw_name'), 'analyte_aliases', ['raw_name'])

    # Create reference_ranges table
    op.create_table(
        'reference_ranges',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('analyte_id', sa.String(36), nullable=False),
        sa.Column('unit', sa.String(50), nullable=False),
        sa.Column('low_normal', sa.Float(), nullable=True),
        sa.Column('high_normal', sa.Float(), nullable=True),
        sa.Column('low_critical', sa.Float(), nullable=True),
        sa.Column('high_critical', sa.Float(), nullable=True),
        sa.Column('sex', sa.String(10), nullable=True),
        sa.Column('age_min_years', sa.Integer(), nullable=True),
        sa.Column('age_max_years', sa.Integer(), nullable=True),
        sa.Column('source', sa.String(255), nullable=True),
        sa.ForeignKeyConstraint(['analyte_id'], ['analyte_catalog.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_reference_ranges_analyte_id'), 'reference_ranges', ['analyte_id'])

    # Create lab_reports table
    op.create_table(
        'lab_reports',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('family_member_id', sa.String(36), nullable=False),
        sa.Column('uploaded_by_user_id', sa.String(36), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=True),
        sa.Column('lab_name', sa.String(255), nullable=True),
        sa.Column('extractor_used', sa.String(100), nullable=True),
        sa.Column('extraction_status', sa.Enum('pending', 'processing', 'success', 'partial', 'failed', name='extractionstatus'), nullable=False, server_default='pending'),
        sa.Column('extraction_notes', sa.Text(), nullable=True),
        sa.Column('raw_patient_name', sa.String(255), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['family_member_id'], ['family_members.id']),
        sa.ForeignKeyConstraint(['uploaded_by_user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_lab_reports_family_member_id'), 'lab_reports', ['family_member_id'])
    op.create_index(op.f('ix_lab_reports_extraction_status'), 'lab_reports', ['extraction_status'])
    op.create_index(op.f('ix_lab_reports_is_deleted'), 'lab_reports', ['is_deleted'])
    op.create_index(op.f('ix_lab_reports_report_date'), 'lab_reports', ['report_date'])

    # Create test_results table
    op.create_table(
        'test_results',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('lab_report_id', sa.String(36), nullable=False),
        sa.Column('family_member_id', sa.String(36), nullable=False),
        sa.Column('analyte_id', sa.String(36), nullable=False),
        sa.Column('report_date', sa.Date(), nullable=True),
        sa.Column('raw_name', sa.String(255), nullable=False),
        sa.Column('raw_value', sa.Float(), nullable=True),
        sa.Column('raw_unit', sa.String(50), nullable=False),
        sa.Column('canonical_value', sa.Float(), nullable=True),
        sa.Column('canonical_unit', sa.String(50), nullable=False),
        sa.Column('ref_low', sa.Float(), nullable=True),
        sa.Column('ref_high', sa.Float(), nullable=True),
        sa.Column('ref_source', sa.String(255), nullable=True),
        sa.Column('is_canonical', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_out_of_range', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['analyte_id'], ['analyte_catalog.id']),
        sa.ForeignKeyConstraint(['family_member_id'], ['family_members.id']),
        sa.ForeignKeyConstraint(['lab_report_id'], ['lab_reports.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_test_results_analyte_id'), 'test_results', ['analyte_id'])
    op.create_index(op.f('ix_test_results_family_member_id'), 'test_results', ['family_member_id'])
    op.create_index(op.f('ix_test_results_lab_report_id'), 'test_results', ['lab_report_id'])
    op.create_index(op.f('ix_test_results_report_date'), 'test_results', ['report_date'])


def downgrade() -> None:
    # Drop all tables in reverse order
    op.drop_table('test_results')
    op.drop_table('lab_reports')
    op.drop_table('reference_ranges')
    op.drop_table('analyte_aliases')
    op.drop_table('analyte_catalog')
    op.drop_table('family_members')
    op.drop_table('families')
    op.drop_table('users')
