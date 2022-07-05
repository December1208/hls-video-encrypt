"""Initial migration.

Revision ID: f670518ef5b8
Revises: 
Create Date: 2022-07-01 17:59:24.291123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f670518ef5b8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('hls_video',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=128), nullable=True),
    sa.Column('identity', sa.String(length=32), nullable=False),
    sa.Column('origin_file_path', sa.Text(), nullable=True),
    sa.Column('file_path', sa.Text(), nullable=True),
    sa.Column('transcoding_finished', sa.Boolean(), nullable=True),
    sa.Column('key', sa.String(length=32), nullable=True),
    sa.Column('iv', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_hls_video_identity'), 'hls_video', ['identity'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_hls_video_identity'), table_name='hls_video')
    op.drop_table('hls_video')
    # ### end Alembic commands ###