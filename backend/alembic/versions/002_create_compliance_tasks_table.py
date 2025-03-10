"""create compliance tasks table

Revision ID: 002
Revises: 001
Create Date: 2025-03-08 23:18:22.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade():
    # Create compliance_tasks table
    op.create_table(
        'compliance_tasks',
        sa.Column('compliance_task_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('deadline', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recurrence', sa.String(), nullable=True),
        sa.Column('dependent_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('state', sa.String(), nullable=False, server_default='Open'),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('assignee_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reviewer_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('approver_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        
        sa.ForeignKeyConstraint(['dependent_task_id'], ['compliance_tasks.compliance_task_id'], ),
        sa.ForeignKeyConstraint(['assignee_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['reviewer_id'], ['users.user_id'], ),
        sa.ForeignKeyConstraint(['approver_id'], ['users.user_id'], ),
        
        # Add check constraints for state and category
        sa.CheckConstraint("state IN ('Open', 'Pending', 'Review Required', 'Completed', 'Overdue')", name='valid_state'),
        sa.CheckConstraint("category IN ('SEBI', 'RBI', 'IT/GST')", name='valid_category')
    )

def downgrade():
    op.drop_table('compliance_tasks')
