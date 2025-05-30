"""add new column in test_type

Revision ID: 0718de390b4a
Revises: a400166c5352
Create Date: 2025-05-24 19:01:26.205146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0718de390b4a'
down_revision: Union[str, None] = 'a400166c5352'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_answers', 'is_correct')
    op.drop_column('test_questions', 'possible_answers')
    op.add_column('test_types', sa.Column('estimated_duration', sa.Integer(), nullable=True, comment='Примерная продолжительность прохождения теста в минутах'))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('test_types', 'estimated_duration')
    op.add_column('test_questions', sa.Column('possible_answers', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('test_answers', sa.Column('is_correct', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
