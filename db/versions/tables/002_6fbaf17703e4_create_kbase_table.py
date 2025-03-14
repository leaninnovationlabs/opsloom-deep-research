"""create kbase_docs table

Revision ID: 6fbaf17703e4
Revises: c84e196eb362
Create Date: 2024-07-25 22:23:03.886068

"""
from typing import Sequence, Union
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.engine.reflection import Inspector

from alembic import op
from backend.api.kbase.kbase_schema import Base, KnowledgeBaseORM


# revision identifiers, used by Alembic.
revision: str = '002_6fbaf17703e4'
down_revision: Union[str, None] = '001_d8c115db18b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    tables = inspector.get_table_names()
    # Only create table if it doesn't exist
    if "kbase" not in tables:
        Base.metadata.create_all(bind=conn, tables=[KnowledgeBaseORM.__table__])
        print("Table 'kbase' created successfully.")
    else:
        print("Table 'kbase' already exists.")

def downgrade():
    op.drop_table('kbase')