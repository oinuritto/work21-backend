"""Add llm_estimation field to projects

Revision ID: add_llm_estimation
Revises: 
Create Date: 2025-12-05 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_llm_estimation'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле llm_estimation в таблицу projects
    op.add_column('projects', sa.Column('llm_estimation', sa.Text(), nullable=True))


def downgrade() -> None:
    # Удаляем поле llm_estimation из таблицы projects
    op.drop_column('projects', 'llm_estimation')

