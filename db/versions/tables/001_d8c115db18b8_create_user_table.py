"""
create user table

Revision ID: 001_d8c115db18b8
Revises: 000_b276689b59
Create Date: 2024-09-13 12:24:31.156466
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# Revision identifiers
revision: str = "001_d8c115db18b8"
down_revision: Union[str, None] = "000_b276689b59"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- Import the ORM base/model from your user_schema ---
from backend.api.auth.user_schema import Base, UserORM

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    # Only create table if it doesn't exist
    if "users" not in tables:
        Base.metadata.create_all(bind=conn, tables=[UserORM.__table__])
        print("Table 'users' created successfully.")
    else:
        print("Table 'users' already exists.")

def downgrade():
    conn = op.get_bind()

    # Drop the 'users' table
    UserORM.__table__.drop(bind=conn)
    print("Table 'users' dropped.")
