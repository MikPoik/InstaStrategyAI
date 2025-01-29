"""Add average engagement metrics columns

Revision ID: add_avg_engagement_metrics
Revises: add_post_texts_column
Create Date: 2025-01-29
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'add_avg_engagement_metrics'
down_revision = 'add_post_texts_column'
branch_labels = None
depends_on = None

def upgrade():
    # Add columns to instagram_profiles table
    op.add_column('instagram_profiles', sa.Column('avg_likes', sa.Float(), nullable=True))
    op.add_column('instagram_profiles', sa.Column('avg_comments', sa.Float(), nullable=True))
    
    # Add columns to similar_accounts table
    op.add_column('similar_accounts', sa.Column('avg_likes', sa.Float(), nullable=True))
    op.add_column('similar_accounts', sa.Column('avg_comments', sa.Float(), nullable=True))

def downgrade():
    # Remove columns from instagram_profiles table
    op.drop_column('instagram_profiles', 'avg_likes')
    op.drop_column('instagram_profiles', 'avg_comments')
    
    # Remove columns from similar_accounts table
    op.drop_column('similar_accounts', 'avg_likes')
    op.drop_column('similar_accounts', 'avg_comments')
