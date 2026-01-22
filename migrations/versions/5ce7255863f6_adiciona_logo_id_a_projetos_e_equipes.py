"""adiciona logo_id a projetos e equipes

Revision ID: 5ce7255863f6
Revises: e3bd26848c17
Create Date: 2026-01-19 23:09:48.636210
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ce7255863f6'
down_revision = 'e3bd26848c17'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('projetos') as batch_op:
        batch_op.add_column(
            sa.Column('logo_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'fk_projetos_logo',
            'imagens',
            ['logo_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    with op.batch_alter_table('equipes') as batch_op:
        batch_op.add_column(
            sa.Column('logo_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'fk_equipes_logo',
            'imagens',
            ['logo_id'],
            ['id'],
            ondelete='RESTRICT'
        )

def downgrade():

    with op.batch_alter_table('equipes') as batch_op:
        batch_op.drop_constraint('fk_equipes_logo', type_='foreignkey')
        batch_op.drop_column('logo_id')

    with op.batch_alter_table('projetos') as batch_op:
        batch_op.drop_constraint('fk_projetos_logo', type_='foreignkey')
        batch_op.drop_column('logo_id')
