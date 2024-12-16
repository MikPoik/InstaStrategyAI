"""Add post_texts column to similar_accounts

Revision ID: add_post_texts_column
Revises: 
Create Date: 2024-12-16
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_post_texts_column'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('similar_accounts', sa.Column('post_texts', sa.Text(), nullable=True))

def downgrade():
    op.drop_column('similar_accounts', 'post_texts')
