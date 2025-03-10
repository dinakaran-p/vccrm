"""create documents tables

Revision ID: 003
Revises: 002
Create Date: 2025-03-09 09:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None

def upgrade():
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('document_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('date_uploaded', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('status', sa.String(), nullable=False, server_default='Active'),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.Column('process_id', sa.String(), nullable=True),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        # Add check constraints for status and category
        sa.CheckConstraint("status IN ('Active', 'Pending Approval', 'Expired')", name='valid_document_status'),
        sa.CheckConstraint("category IN ('Contribution Agreement', 'KYC', 'Notification', 'Report', 'Other')", name='valid_document_category')
    )
    
    # Create task_documents table
    op.create_table(
        'task_documents',
        sa.Column('task_document_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('compliance_task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        sa.ForeignKeyConstraint(['compliance_task_id'], ['compliance_tasks.compliance_task_id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.document_id'], ),
        
        # Add unique constraint to prevent duplicate document-task associations
        sa.UniqueConstraint('compliance_task_id', 'document_id', name='uq_task_document')
    )
    
    # Add indexes for commonly queried fields
    op.create_index('idx_document_name', 'documents', ['name'])
    op.create_index('idx_document_category', 'documents', ['category'])
    op.create_index('idx_document_status', 'documents', ['status'])
    op.create_index('idx_document_date_uploaded', 'documents', ['date_uploaded'])

def downgrade():
    op.drop_table('task_documents')
    op.drop_table('documents')
