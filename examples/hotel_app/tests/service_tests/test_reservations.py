import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.db.models import Guest, Reservation, Room
from backend.db.repositories.reservation import ReservationRepository
from backend.schemas.reservation import ReservationSchema
from datetime import datetime

# 1) Create a fixture that seeds a single Guest with a known UUID, then seeds 10 Reservations for that guest.
@pytest_asyncio.fixture
async def seed_reservations_fixture(async_session: AsyncSession):
    """
    Truncates relevant tables and seeds:
      - 1 Guest with a known GUEST_UUID
      - 1 Room (optionally) or multiple Rooms
      - 10 Reservations referencing that GUEST_UUID
    Returns the (guest_uuid) for the tests to use.
    """

    # Clean up everything. SQLite doesn't support TRUNCATE, use DELETE instead
    await async_session.execute(text("DELETE FROM service_orders"))
    await async_session.execute(text("DELETE FROM reservations"))
    await async_session.execute(text("DELETE FROM messages"))
    await async_session.execute(text("DELETE FROM sessions"))
    
    # Don't delete rooms and guests - they're already seeded by initialize_database()
    # We'll just add our test guest with a known UUID
    
    # Commit the deletes
    await async_session.commit()

    # Insert a single guest with a known UUID (as a string for SQLite)
    GUEST_UUID = "12345678-1234-5678-1234-567812345678"

    guest = Guest(
        guest_id=GUEST_UUID,
        full_name="Test Guest",
        email="test.guest@example.com"
    )
    async_session.add(guest)

    # We don't need to insert a room because they're already seeded in initialize_database()
    await async_session.commit()

    # Now insert 10 reservations referencing that guest + room
    reservations_to_add = []
    for i in range(10):
        r = Reservation(
            guest_id=GUEST_UUID,   # Must match the inserted Guest
            room_id=101,           # Must match an existing Room
            check_in=datetime(2025, 1, 15 + i, 14, 0, 0),
            check_out=datetime(2025, 1, 16 + i, 11, 0, 0),
            status="confirmed"
        )
        reservations_to_add.append(r)

    async_session.add_all(reservations_to_add)
    await async_session.commit()

    # Return the guest UUID so tests can reference it
    return GUEST_UUID


@pytest.mark.asyncio
async def test_list_reservations_returns_list_of_reservation_schema(
    async_session: AsyncSession, 
    seed_reservations_fixture: str
):
    """
    'list_reservations' should return the 10 seeded reservations
    """
    repo = ReservationRepository(db=async_session)
    reservations = await repo.list_reservations()
    assert len(reservations) >= 10, f"Expected at least 10, got {len(reservations)}"
    assert isinstance(reservations[0], ReservationSchema)


@pytest.mark.asyncio
async def test_list_reservations_by_guest_id_returns_list_of_reservation_schema(
    async_session: AsyncSession, 
    seed_reservations_fixture: str
):
    """
    'list_reservations_by_guest_id' should return reservations for the seeded guest.
    We'll expect all 10 to match.
    """
    guest_uuid = seed_reservations_fixture
    repo = ReservationRepository(db=async_session)
    
    reservations = await repo.list_reservations_by_guest_id(guest_uuid)
    assert len(reservations) == 10, f"Expected 10 reservations for that guest, got {len(reservations)}"
    assert isinstance(reservations[0], ReservationSchema)

@pytest.mark.asyncio
async def test_return_empty_list_for_nonexistent_guest_id(async_session: AsyncSession, seed_reservations_fixture):
    """
    If we pass a random UUID that doesn't exist, we expect 0 reservations.
    """
    repo = ReservationRepository(db=async_session)
    fake_uuid = str(uuid.uuid4())  # random nonexistent as string

    reservations = await repo.list_reservations_by_guest_id(fake_uuid)
    assert len(reservations) == 0, "Expected an empty list"


@pytest.mark.asyncio
async def test_create_reservation(async_session: AsyncSession, seed_reservations_fixture):
    """
    Create a new reservation for the same seeded guest.
    """
    guest_uuid = seed_reservations_fixture
    repo = ReservationRepository(db=async_session)

    # Make sure to use a string UUID
    new_res = ReservationSchema(
        guest_id=guest_uuid,  # This is already a string from the fixture
        room_id=101,
        check_in=datetime(2027, 10, 1, 14, 0, 0),
        check_out=datetime(2027, 10, 2, 12, 0, 0),
        status="confirmed"
    )
    created_reservation = await repo.create_reservation(new_res)
    assert isinstance(created_reservation, ReservationSchema)
    assert created_reservation.reservation_id is not None


@pytest.mark.asyncio
async def test_create_reservation_invalid_date(async_session: AsyncSession, seed_reservations_fixture):
    """
    Should raise ValueError if check_in >= check_out
    """
    guest_uuid = seed_reservations_fixture
    repo = ReservationRepository(db=async_session)

    new_res = ReservationSchema(
        guest_id=guest_uuid,  # This is already a string from the fixture
        room_id=101,
        check_in=datetime(1999, 10, 2, 14, 0, 0),
        check_out=datetime(1999, 10, 1, 12, 0, 0),
        status="confirmed"
    )

    with pytest.raises(ValueError, match="check_in must be before check_out"):
        await repo.create_reservation(new_res)