"""migration

Revision ID: 1382220b9dd9
Revises: 766c435c74f1
Create Date: 2024-11-25 21:04:26.827075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1382220b9dd9'
down_revision: Union[str, None] = '766c435c74f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('receipt_id', sa.Integer(), nullable=False))
    op.drop_constraint('fk_items_user_id_users', 'items', type_='foreignkey')
    op.create_foreign_key(None, 'items', 'receipts', ['receipt_id'], ['id'])
    op.drop_column('items', 'user_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'items', type_='foreignkey')
    op.create_foreign_key('fk_items_user_id_users', 'items', 'users', ['user_id'], ['id'])
    op.drop_column('items', 'receipt_id')
    # ### end Alembic commands ###
