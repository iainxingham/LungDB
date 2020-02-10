"""Added physiology table - height and weight

Revision ID: 7126981c7bae
Revises: 7a1c1908f800
Create Date: 2020-02-10 16:32:30.628084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7126981c7bae'
down_revision = '7a1c1908f800'
branch_labels = None
depends_on = None


def upgrade():
    # pylint: disable=no-member
    op.create_table('physiology',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('study_date', sa.Date(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['subject_id'], ['patient.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # pylint: disable=no-member
    op.drop_table('physiology')
