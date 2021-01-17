"""init federation with ActivityPub Actor

Revision ID: 8842c351a2d8
Revises: 4e8597c50064
Create Date: 2021-01-10 16:02:43.811023

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8842c351a2d8'
down_revision = '4e8597c50064'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'app_config',
        sa.Column(
            'federation_enabled', sa.Boolean(), nullable=True, default=False
        ),
    )
    op.execute('UPDATE app_config SET federation_enabled = true')
    op.alter_column('app_config', 'federation_enabled', nullable=False)

    op.create_table('actors',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ap_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.Enum('Application', 'Group', 'Person', name='actor_types'), server_default='Person', nullable=True),
        sa.Column('domain', sa.String(length=1000), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('preferred_username', sa.String(length=255), nullable=False),
        sa.Column('public_key', sa.String(length=5000), nullable=True),
        sa.Column('private_key', sa.String(length=5000), nullable=True),
        sa.Column('inbox_url', sa.String(length=255), nullable=False),
        sa.Column('outbox_url', sa.String(length=255), nullable=False),
        sa.Column('followers_url', sa.String(length=255), nullable=False),
        sa.Column('following_url', sa.String(length=255), nullable=False),
        sa.Column('shared_inbox_url', sa.String(length=255), nullable=False),
        sa.Column('is_remote', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('manually_approves_followers', sa.Boolean(), nullable=False),
        sa.Column('last_fetch_date', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ap_id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade():
    op.drop_table('actors')
    op.execute('DROP TYPE actor_types')

    op.drop_column('app_config', 'federation_enabled')