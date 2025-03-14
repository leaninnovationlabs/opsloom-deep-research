import asyncio
import uuid
from datetime import datetime, timedelta
from sqlalchemy import select, text

from sqlalchemy.ext.asyncio import AsyncEngine
from contextlib import asynccontextmanager

from backend.db.models import Base, Room, Guest, Reservation, Service
from backend.db.session import engine, async_session_maker


async def create_tables(db_engine: AsyncEngine = engine):
    """Create all tables in the in-memory database"""
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully in in-memory database")


async def seed_rooms():
    """Seed the rooms table with initial data"""
    async with async_session_maker() as session:
        # Check if rooms already exist
        result = await session.execute(select(Room).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Rooms already exist, skipping seeding")
            return
            
        # Add single rooms
        for room_num in range(101, 111):
            session.add(Room(
                room_id=room_num,
                room_type="single",
                rate=100.00
            ))
        
        # Add double rooms
        for room_num in range(111, 121):
            session.add(Room(
                room_id=room_num,
                room_type="double",
                rate=200.00
            ))
        
        # Add suite rooms
        for room_num in range(121, 131):
            session.add(Room(
                room_id=room_num,
                room_type="suite",
                rate=300.00
            ))
        
        await session.commit()
    print("Rooms seeded successfully")


async def seed_services():
    """Seed the services table with initial data"""
    async with async_session_maker() as session:
        # Check if services already exist
        result = await session.execute(select(Service).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Services already exist, skipping seeding")
            return
            
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
            session.add(Service(
                name=svc["name"],
                description=svc["description"],
                price=svc["price"]
            ))
        
        await session.commit()
    print("Services seeded successfully")


async def seed_guests_and_reservations():
    """Seed guests and reservations tables"""
    async with async_session_maker() as session:
        # Check if guests already exist
        result = await session.execute(select(Guest).limit(1))
        if result.scalar_one_or_none() is not None:
            print("Guests already exist, skipping seeding")
            return
            
        guests = [
            ("Peter Griffin",        "peter.griffin@quahog.com",         "(715) 555-0101"),
            ("Lois Griffin",         "lois.griffin@quahog.com",          "(715) 555-0102"),
            ("Chris Griffin",        "chris.griffin@quahog.net",         "(715) 555-0103"),
            ("Meg Griffin",          "meg.griffin@quahog.com",           "(715) 555-0104"),
            ("Stewie Griffin",       "stewie.griffin@quahog.org",        "(715) 555-0105"),
            ("Brian Griffin",        "brian.griffin@quahog.com",         "(715) 555-0106"),
            ("Cleveland Brown",      "cleveland.brown@quahog.com",       "(715) 555-0107"),
            ("Joe Swanson",          "joe.swanson@quahog.net",           "(715) 555-0108"),
            ("Glenn Quagmire",       "glenn.quagmire@quahog.com",        "(715) 555-0109"),
            ("Bonnie Swanson",       "bonnie.swanson@quahog.com",        "(715) 555-0110"),
        ]
        
        inserted_guest_ids = []
        
        # Insert guests
        for full_name, email, phone in guests:
            guest_id = str(uuid.uuid4())
            session.add(Guest(
                guest_id=guest_id,
                full_name=full_name,
                email=email,
                phone=phone
            ))
            inserted_guest_ids.append(guest_id)
        
        await session.commit()
        
        # Insert reservations for the first 10 guests
        start_date = datetime.now()
        for i, guest_id in enumerate(inserted_guest_ids[:10]):
            room_id = 101 + i
            check_in = start_date + timedelta(days=i)
            check_out = check_in + timedelta(days=5)
            
            session.add(Reservation(
                guest_id=guest_id,
                room_id=room_id,
                check_in=check_in,
                check_out=check_out,
                status="confirmed"
            ))
        
        await session.commit()
    print("Guests and reservations seeded successfully")


async def initialize_database():
    """Initialize the database with tables and seed data"""
    await create_tables()
    await seed_rooms()
    await seed_services()
    await seed_guests_and_reservations()
    print("In-memory database initialized successfully")


@asynccontextmanager
async def lifespan(app):
    """
    FastAPI lifespan context manager to initialize the in-memory database.
    """
    print("Initializing in-memory SQLite database...")
    await initialize_database()
    
    yield
    
    # Nothing to do when the app is shutting down - in-memory DB disappears automatically


if __name__ == "__main__":
    # Run this directly to test the database initialization
    asyncio.run(initialize_database())