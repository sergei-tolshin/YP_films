"""create partition
Revision ID: 3b250d3ef63a
Revises: ab1ff1fe180b
Create Date: 2022-04-27 17:09:28.114739
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3b250d3ef63a'
down_revision = 'ab1ff1fe180b'
branch_labels = None
depends_on = None


def upgrade():
    # ### end Alembic commands ###
    op.execute("""CREATE TABLE IF NOT EXISTS "user_history_pc" 
                  PARTITION OF "user_history" FOR VALUES IN ('pc');""")

    op.execute("""CREATE TABLE IF NOT EXISTS "user_history_mobile" 
                  PARTITION OF "user_history" FOR VALUES IN ('mobile');""")

    op.execute("""CREATE TABLE IF NOT EXISTS "user_history_tablet" 
                  PARTITION OF "user_history" FOR VALUES IN ('tablet');""")


def downgrade():
    op.drop_table('user_history_pc')
    op.drop_table('user_history_mobile')
    op.drop_table('user_history_tablet')
