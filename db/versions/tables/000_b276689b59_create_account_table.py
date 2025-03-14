"""
create account table

Revision ID: 000_b276689b59
Revises:
Create Date: 2024-09-13 12:10:08.348062
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "000_b276689b59"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Import your ORM + Base from your existing account_schema file
from backend.api.account.account_schema import Base, AccountORM


def upgrade():
    # Acquire the current DB connection
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    # Only create the table if it does not exist
    if "account" not in tables:
        # Create the "account" table from the ORM definition
        Base.metadata.create_all(bind=conn, tables=[AccountORM.__table__])
        print("Table 'account' created successfully.")


def downgrade():
    conn = op.get_bind()

    # Drop just the "account" table
    # (no need to inspect if it exists; dropping a non-existent table is typically safe,
    # or you can add a check if you prefer)
    AccountORM.__table__.drop(bind=conn)
