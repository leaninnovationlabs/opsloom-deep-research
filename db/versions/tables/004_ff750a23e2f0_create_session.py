"""create session and app_config

Revision ID: ff750a23e2f0
Revises: 6fbaf17703e4
Create Date: 2024-07-25 22:49:35.201736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

from backend.api.session.session_schema import Base, SessionORM

# revision identifiers, used by Alembic.
revision: str = '004_ff750a23e2f0'
down_revision: Union[str, None] = '003_87xaf17703e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Use the Inspector to check if the table already exists
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    table_names = inspector.get_table_names()

    if "session" not in table_names:
        Base.metadata.create_all(bind=conn, tables=[SessionORM.__table__])
        print("Table 'session' created successfully.")
    else:
        print("Table 'session' already exists.")

def downgrade():
    
    # Then drop the tables
    op.drop_table('session')
