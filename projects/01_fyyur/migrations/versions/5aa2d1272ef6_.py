"""empty message

Revision ID: 5aa2d1272ef6
Revises: 5d7c99e1c353
Create Date: 2020-01-23 19:55:15.489539

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5aa2d1272ef6'
down_revision = '5d7c99e1c353'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('created_ts', sa.DateTime(), nullable=True))
    op.add_column('venues', sa.Column('created_ts', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venues', 'created_ts')
    op.drop_column('artists', 'created_ts')
    # ### end Alembic commands ###
