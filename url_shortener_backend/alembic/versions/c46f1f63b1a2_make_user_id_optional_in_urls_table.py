"""Make user_id optional in Urls table

Revision ID: c46f1f63b1a2
Revises: f2c12b22d5ff
Create Date: 2024-09-10 12:42:07.940030

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c46f1f63b1a2'
down_revision: Union[str, None] = 'f2c12b22d5ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('urls', sa.Column('user_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('urls', 'user_id')
    # ### end Alembic commands ###
