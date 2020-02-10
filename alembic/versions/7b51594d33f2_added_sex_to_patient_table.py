"""Added sex to patient table

Revision ID: 7b51594d33f2
Revises: 7126981c7bae
Create Date: 2020-02-10 18:01:57.961962

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b51594d33f2'
down_revision = '7126981c7bae'
branch_labels = None
depends_on = None


def upgrade():
    # pylint: disable=no-member
    op.add_column('patient', sa.Column('sex', sa.String(length=10), nullable=True))


def downgrade():
    # pylint: disable=no-member
    op.drop_column('patient', 'sex')
