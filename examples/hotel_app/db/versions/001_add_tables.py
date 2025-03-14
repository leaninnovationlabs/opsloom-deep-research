"""
create hotel schema

Revision ID: 0001_hotel_schema
Revises: 
Create Date: 2025-01-08
"""

from typing import Sequence, Union
from alembic import op
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "0001_hotel_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Import your ORM Base and models
from backend.db.models import Base, Room, Guest, Reservation, Service, ServiceOrders, Session, MessagePair


def upgrade():
    conn = op.get_bind()

    # 1) Enable needed extensions (if Postgres)
    # CITEXT for case-insensitive text
    op.execute("CREATE EXTENSION IF NOT EXISTS citext")
    # pgcrypto for gen_random_uuid() (if you rely on the default= text('gen_random_uuid()'))
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # 2) Optionally check if certain tables exist before creating. 
    #    Typically, you can just create all because Alembic is controlling versions.
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # 3) Create all tables for the imported Base
    Base.metadata.create_all(bind=conn, tables=[Room.__table__, Guest.__table__, Reservation.__table__, Service.__table__, ServiceOrders.__table__, Session.__table__, MessagePair.__table__])

    print("Tables created successfully (rooms, guests, reservations, services, service_orders, sessions, messages).")


def downgrade():
    conn = op.get_bind()

    # If you want to drop only the tables you created in this revision,
    # you can pass them explicitly in reverse dependency order.
    # For simplicity, let's drop them all at once:
    Base.metadata.drop_all(bind=conn, tables=[Room.__table__, Guest.__table__, Reservation.__table__, Service.__table__, ServiceOrders.__table__, Session.__table__, MessagePair.__table__])

    # Then optionally drop the extensions if you only want them for this schema
    op.execute("DROP EXTENSION IF EXISTS citext")
    op.execute("DROP EXTENSION IF EXISTS pgcrypto")

    print("Tables and extensions dropped successfully.")
