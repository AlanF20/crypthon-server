"""haciendo opcional img

Revision ID: 5c92b59d3f95
Revises: efc7931987e4
Create Date: 2023-11-30 22:17:58.766771

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5c92b59d3f95'
down_revision = 'efc7931987e4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crypto_currency', schema=None) as batch_op:
        batch_op.alter_column('cryptoImg',
               existing_type=sa.TEXT(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('crypto_currency', schema=None) as batch_op:
        batch_op.alter_column('cryptoImg',
               existing_type=sa.TEXT(),
               nullable=False)

    # ### end Alembic commands ###
