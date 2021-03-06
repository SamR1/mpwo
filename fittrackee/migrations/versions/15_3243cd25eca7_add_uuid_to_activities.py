"""add uuid to activities

Revision ID: 3243cd25eca7
Revises: 8a0aad4c838c
Create Date: 2020-12-30 14:54:45.568864

"""
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '3243cd25eca7'
down_revision = '8a0aad4c838c'
branch_labels = None
depends_on = None


def upgrade():
    connection = op.get_bind()
    activities_helper = sa.Table(
        'activities',
        sa.MetaData(),
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False),
    )

    op.add_column(
        'activities',
        sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_unique_constraint('activities_uuid_key', 'activities', ['uuid'])
    op.add_column(
        'activity_segments',
        sa.Column(
            'activity_uuid', postgresql.UUID(as_uuid=True), nullable=True
        ),
    )
    op.add_column(
        'records',
        sa.Column(
            'activity_uuid', postgresql.UUID(as_uuid=True), nullable=True
        ),
    )
    for activity in connection.execute(activities_helper.select()):
        activity_uuid = uuid4()
        op.execute(
            f"UPDATE activities SET uuid = '{activity_uuid}' "
            f"WHERE activities.id = {activity.id}"
        )
        op.execute(
            f"UPDATE records SET activity_uuid = '{activity_uuid}' "
            f"WHERE records.activity_id = {activity.id}"
        )
        op.execute(
            f"UPDATE activity_segments SET activity_uuid = '{activity_uuid}' "
            f"WHERE activity_segments.activity_id = {activity.id}"
        )

    op.alter_column('activities', 'uuid', nullable=False)
    op.alter_column('activity_segments', 'activity_uuid', nullable=False)
    op.alter_column('records', 'activity_uuid', nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('records', 'activity_uuid')
    op.drop_column('activity_segments', 'activity_uuid')
    op.drop_constraint('activities_uuid_key', 'activities', type_='unique')
    op.drop_column('activities', 'uuid')
    # ### end Alembic commands ###
