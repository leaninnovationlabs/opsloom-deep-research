"""create kbase_docs table

Revision ID: 6fbaf17703e4
Revises: c84e196eb362
Create Date: 2024-07-25 22:23:03.886068

"""
from typing import Sequence, Union
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.engine.reflection import Inspector

from alembic import op

from backend.api.assistant.assistant_schema import Base, AssistantORM

# revision identifiers, used by Alembic.
revision: str = '003_87xaf17703e4'
down_revision: Union[str, None] = '002_6fbaf17703e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    table_names = inspector.get_table_names()

    if "assistant" not in table_names:
        Base.metadata.create_all(bind=conn, tables=[AssistantORM.__table__])
        print("Table 'assistant' created successfully.")
    else:
        print("Table 'assistant' already exists.")


def downgrade():
    op.drop_table('assistant')