"""add agent message table which stores JSON array of all messages in an agent run

Revision ID: cf0151f104d6
Revises: 795abb481236
Create Date: 2025-01-22 14:35:06.859923

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

from backend.api.chat.chat_schema import Base, AgentMessageORM


# revision identifiers, used by Alembic.
revision: str = 'cf0151f104d6'
down_revision: Union[str, None] = '795abb481236'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Use the Inspector to check if the table already exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    table_names = inspector.get_table_names()

    if "agent_message" not in table_names:
        Base.metadata.create_all(bind=conn, tables=[AgentMessageORM.__table__])
        print("Table 'agent_message' created successfully.")
    else:
        print("Table 'agent_message' already exists.")

def downgrade():
    
    # Then drop the tables
    op.drop_table('agent_message')
