"""Add assignee_id field to projects

Revision ID: add_assignee_to_projects
Revises: add_llm_estimation
Create Date: 2025-01-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_assignee_to_projects'
down_revision = 'add_llm_estimation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Добавляем поле assignee_id в таблицу projects
    op.add_column('projects', sa.Column('assignee_id', sa.Integer(), nullable=True))
    # Добавляем внешний ключ
    op.create_foreign_key(
        'fk_projects_assignee_id_users',
        'projects',
        'users',
        ['assignee_id'],
        ['id']
    )


def downgrade() -> None:
    # Удаляем внешний ключ
    op.drop_constraint('fk_projects_assignee_id_users', 'projects', type_='foreignkey')
    # Удаляем поле assignee_id из таблицы projects
    op.drop_column('projects', 'assignee_id')

