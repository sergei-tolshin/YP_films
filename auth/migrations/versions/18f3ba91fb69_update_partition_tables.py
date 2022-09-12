"""update partition tables
Revision ID: 7db8ae2bf4e6
Revises: 3b250d3ef63a
Create Date: 2022-04-27 17:15:53.849017
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7db8ae2bf4e6'
down_revision = '3b250d3ef63a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_foreign_key(
        op.f('fk__user_history_pc__user_id__users'),
        'user_history_pc', 'users', ['user'], ['uuid']
    )
    op.create_foreign_key(
        op.f('fk__user_history_mobile__user_id__users'),
        'user_history_mobile', 'users', ['user'], ['uuid']
    )
    op.create_foreign_key(
        op.f('fk__user_history_tablet__user_id__users'),
        'user_history_tablet', 'users', ['user'], ['uuid']
    )

    op.create_primary_key(
        op.f('pk__user_history_pc'), 'user_history_pc', ['platform', 'uuid']
    )
    op.create_primary_key(
        op.f('pk__user_history_mobile'), 'user_history_mobile', ['platform', 'uuid']
    )
    op.create_primary_key(
        op.f('pk__user_history_tablet'), 'user_history_tablet', ['platform', 'uuid']
    )


def downgrade():
    op.drop_constraint(
        op.f('fk__user_history_pc__user_id__users'),
        'user_history_pc', type_='foreignkey'
    )
    op.drop_constraint(
        op.f('fk__user_history_mobile__user_id__users'),
        'user_history_mobile', type_='foreignkey'
    )
    op.drop_constraint(
        op.f('fk__user_history_tablet__user_id__users'),
        'user_history_tablet', type_='foreignkey'
    )
    op.drop_constraint(
        op.f('pk__user_history_pc'), 'user_history_pc', type_='foreignkey'
    )
    op.drop_constraint(
        op.f('pk__user_history_mobile'), 'user_history_mobile', type_='foreignkey'
    )
    op.drop_constraint(
        op.f('pk__user_history_tablet'), 'user_history_tablet', type_='foreignkey'
    )
