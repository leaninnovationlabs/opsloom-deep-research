"""add_kbase_docs

Revision ID: 95fce5bd97c2
Revises: cf0151f104d6
Create Date: 2025-02-01 12:14:11.136284

"""
from typing import Sequence, Union
from sqlalchemy import UUID, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.engine.reflection import Inspector

from alembic import op
from backend.api.kbase.kbase_schema import Base, KbaseDocumentORM

# revision identifiers, used by Alembic.
revision: str = '95fce5bd97c2'
down_revision: Union[str, None] = 'cf0151f104d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    tables = inspector.get_table_names()
    # Only create table if it doesn't exist
    if "kbase_documents" not in tables:
        Base.metadata.create_all(bind=conn, tables=[KbaseDocumentORM.__table__])
        print("Table 'kbase_documents' created successfully.")
    else:
        print("Table 'kbase_documents' already exists.")

def downgrade():
    op.drop_table('kbase_documents')