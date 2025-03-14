"""
seed_data

Revision ID: 0002_seed_data
Revises: 0001_hotel_schema
Create Date: 2025-01-08
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = "0002_seed_data"
down_revision: Union[str, None] = "0001_hotel_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()

    # --- Seed Rooms ---
    #   10 single: 101..110, rate=100.00
    #   10 double: 111..120, rate=200.00
    #   10 suite:  121..130, rate=300.00

    # Insert single rooms
    for room_num in range(101, 111):
        conn.execute(
            sa.text(
                """
                INSERT INTO rooms (room_id, room_type, rate)
                VALUES (:room_id, :room_type, :rate)
                """
            ),
            {
                "room_id": room_num,
                "room_type": "single",
                "rate": 100.00
            }
        )

    # Insert double rooms
    for room_num in range(111, 121):
        conn.execute(
            sa.text(
                """
                INSERT INTO rooms (room_id, room_type, rate)
                VALUES (:room_id, :room_type, :rate)
                """
            ),
            {
                "room_id": room_num,
                "room_type": "double",
                "rate": 200.00
            }
        )

    # Insert suite rooms
    for room_num in range(121, 131):
        conn.execute(
            sa.text(
                """
                INSERT INTO rooms (room_id, room_type, rate)
                VALUES (:room_id, :room_type, :rate)
                """
            ),
            {
                "room_id": room_num,
                "room_type": "suite",
                "rate": 300.00
            }
        )

    # --- Seed Services ---
    services = [
        {
            "name": "room service",
            "price": 199.99,
            "description": "Sumptuous meals and beverages delivered right to your room anytime.",
        },
        {
            "name": "room service with hot meal",
            "price": 249.99,
            "description": "One of our savory meals is warmed in the microwave and brought to your door.",
        },
        {
            "name": "wake up call",
            "price": 299.99,
            "description": "One of our staff members will enter your room and call you with your bedside phone.",
        },
        {
            "name": "late check in",
            "price": 349.99,
            "description": "Arrive well past midnight? We'll hold the room.",
        },
        {
            "name": "phone use",
            "price": 19.99,
            "description": "limited phone use for calling one of the allowed phone numbers (see desk for more information)",
        },
        {
            "name": "unstained towel",
            "price": 9.99,
            "description": "towel stolen from the hotel across the street",
        },
        {
            "name": "supervised visit",
            "price": 49.99,
            "description": "A staff member will observe you while you speak with a chosen guest for no more than 20 minutes.",
        },
        {
            "name": "tour in local waste treatment facility",
            "price": 99.99,
            "description": "A guided tour of the local waste treatment facility, including a complimentary gas mask.",
        },
        {
            "name": "hot water",
            "price": 212.99,
            "description": "Limited access to hot water. You will be assigned a two-hour window for hot water use.",
        },
        {
            "name": "electricity",
            "price": 99.99,
            "description": "Keep the lights on as long as you'd like—our power grid, your wallet!",
        },
    ]

    for svc in services:
        conn.execute(
            sa.text(
                """
                INSERT INTO services (name, description, price)
                VALUES (:name, :description, :price)
                """
            ),
            {
                "name": svc["name"],
                "description": svc["description"],
                "price": svc["price"],
            }
        )

def downgrade():
    op.execute("DELETE FROM services")
    op.execute("DELETE FROM rooms")
