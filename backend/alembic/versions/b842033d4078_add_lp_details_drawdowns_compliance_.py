"""add_lp_details_drawdowns_compliance_records_tables

Revision ID: b842033d4078
Revises: 004
Create Date: 2025-03-09 20:29:41.437390

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = 'b842033d4078'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create lp_details table
    op.create_table(
        'lp_details',
        sa.Column('lp_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lp_name', sa.String(), nullable=False),
        sa.Column('mobile_no', sa.String(20)),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('address', sa.Text()),
        sa.Column('nominee', sa.String()),
        sa.Column('pan', sa.String(20)),
        sa.Column('dob', sa.Date()),
        sa.Column('doi', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(10)),
        sa.Column('date_of_agreement', sa.Date()),
        sa.Column('commitment_amount', sa.Numeric(15, 2)),
        sa.Column('acknowledgement_of_ppm', sa.Boolean(), default=False),
        sa.Column('dpid', sa.String(50)),
        sa.Column('client_id', sa.String(50)),
        sa.Column('cml', sa.String(50)),
        sa.Column('isin', sa.String(50)),
        sa.Column('class_of_shares', sa.String(20)),
        sa.Column('citizenship', sa.String(50)),
        sa.Column('type', sa.String(50)),
        sa.Column('geography', sa.String(50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('lp_id')
    )
    
    # Create lp_drawdowns table
    op.create_table(
        'lp_drawdowns',
        sa.Column('drawdown_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('lp_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('drawdown_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Numeric(15, 2), nullable=False),
        sa.Column('drawdown_percentage', sa.Numeric(5, 2)),
        sa.Column('payment_due_date', sa.Date(), nullable=False),
        sa.Column('payment_received_date', sa.Date(), nullable=True),
        sa.Column('payment_status', sa.String(50), nullable=False, server_default='Pending'),
        sa.Column('reference_number', sa.String(100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['lp_id'], ['lp_details.lp_id'], ),
        sa.PrimaryKeyConstraint('drawdown_id')
    )
    
    # Create compliance_records table
    op.create_table(
        'compliance_records',
        sa.Column('record_id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('lp_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('compliance_type', sa.String(), nullable=False),
        sa.Column('compliance_status', sa.String(), nullable=False, server_default='Pending Review'),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('comments', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['lp_id'], ['lp_details.lp_id'], ),
        sa.ForeignKeyConstraint(['updated_by'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('record_id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('ix_lp_details_email'), 'lp_details', ['email'], unique=True)
    op.create_index(op.f('ix_lp_details_pan'), 'lp_details', ['pan'], unique=True)
    op.create_index(op.f('ix_lp_drawdowns_lp_id'), 'lp_drawdowns', ['lp_id'], unique=False)
    op.create_index(op.f('ix_compliance_records_lp_id'), 'compliance_records', ['lp_id'], unique=False)
    op.create_index(op.f('ix_compliance_records_entity_type'), 'compliance_records', ['entity_type'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_compliance_records_entity_type'), table_name='compliance_records')
    op.drop_index(op.f('ix_compliance_records_lp_id'), table_name='compliance_records')
    op.drop_index(op.f('ix_lp_drawdowns_lp_id'), table_name='lp_drawdowns')
    op.drop_index(op.f('ix_lp_details_pan'), table_name='lp_details')
    op.drop_index(op.f('ix_lp_details_email'), table_name='lp_details')
    
    # Drop tables
    op.drop_table('compliance_records')
    op.drop_table('lp_drawdowns')
    op.drop_table('lp_details')
