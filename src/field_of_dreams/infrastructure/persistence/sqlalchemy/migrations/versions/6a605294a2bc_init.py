"""init

Revision ID: 6a605294a2bc
Revises: 
Create Date: 2023-03-04 12:48:07.822261

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a605294a2bc'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_chats_id'), 'chats', ['id'], unique=True)
    op.create_table('users',
    sa.Column('id', sa.BIGINT(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=True)
    op.create_table('words',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(), nullable=False),
    sa.Column('question', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_words_id'), 'words', ['id'], unique=True)
    op.create_table('games',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('word_id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.BIGINT(), nullable=False),
    sa.Column('current_turn_id', sa.Integer(), nullable=True),
    sa.Column('state', sa.Enum('PREPARING', 'STARTED', 'FINISHED', name='gamestate'), nullable=False),
    sa.Column('guessed_letters', sa.ARRAY(sa.CHAR()), nullable=False),
    sa.Column('failed_letters', sa.ARRAY(sa.CHAR()), nullable=False),
    sa.Column('start_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.Column('end_time', sa.TIMESTAMP(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['current_turn_id'], ['players_turns.id'], ondelete='CASCADE', use_alter=True),
    sa.ForeignKeyConstraint(['word_id'], ['words.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('players',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('game_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.BIGINT(), nullable=False),
    sa.Column('state', sa.Enum('WINNER', 'LOSER', 'PLAYING', name='playerstate'), nullable=False),
    sa.Column('joined_at', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('game_id', 'user_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('players_turns',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.UUID(), nullable=False),
    sa.Column('state', sa.Enum('PASSED', 'FAILED', 'IN_PROGRESS', name='turnstate'), nullable=False),
    sa.Column('start_time', sa.TIMESTAMP(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('players_turns')
    op.drop_table('players')
    op.drop_table('games')
    op.drop_index(op.f('ix_words_id'), table_name='words')
    op.drop_table('words')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_chats_id'), table_name='chats')
    op.drop_table('chats')
    # ### end Alembic commands ###