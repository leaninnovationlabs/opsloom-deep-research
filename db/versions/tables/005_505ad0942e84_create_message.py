"""create message

Revision ID: 005_505ad0942e84
Revises: 004_ff750a23e2f0
Create Date: 2024-07-25 22:49:17.130244

"""
from typing import Sequence, Union
from sqlalchemy.engine.reflection import Inspector

from alembic import op
import sqlalchemy as sa
from sqlalchemy import ForeignKey

from backend.api.chat.chat_schema import Base, MessageORM


# revision identifiers, used by Alembic.
revision: str = '005_505ad0942e84'
down_revision: Union[str, None] = '004_ff750a23e2f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    table_names = inspector.get_table_names()

    if "message" not in table_names:
        Base.metadata.create_all(bind=conn, tables=[MessageORM.__table__])
        print("Table 'message' created successfully.")
    else:
        print("Table 'message' already exists.")
def downgrade():
    op.drop_table('message')
