# tests/service_tests/test_session.py

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4

# -------------------------
# Assume these are your models (or import them from your DB models module)
# Adjust import paths as needed.
from backend.db.models import Guest, Session

# Assume this is your service layer and schema:
from backend.services.session import SessionService
from backend.schemas.session import SessionSchema

# -------------------------
# Local test fixture that seeds the DB with one known guest (guest_id=GUEST_UUID)
# and one known session (session_id=SESSION_UUID) referencing that guest.
# This fixture does not live in conftest.py, so it only affects *this file*.
# -------------------------

@pytest_asyncio.fixture
async def seed_guest_and_session(async_session: AsyncSession):
    """
    Clears 'guests' and 'sessions' tables, then inserts:
      - Guest with guest_id=GUEST_UUID
      - Session with session_id=SESSION_UUID, referencing GUEST_UUID
    This ensures each test has a consistent starting point.
    """
    # 1) Delete tables (SQLite doesn't support TRUNCATE)
    await async_session.execute(text("DELETE FROM sessions"))
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()

    # 2) Define known UUIDs for seeding
    GUEST_UUID = "11111111-1111-1111-1111-111111111111"
    SESSION_UUID = "22222222-2222-2222-2222-222222222222"

    # 3) Insert a Guest row with that UUID
    guest = Guest(
        guest_id=GUEST_UUID,          # must match DB column for the guests table
        full_name="Test Guest with UUID",
        email="test.guest.uuid@example.com",
    )
    async_session.add(guest)
    await async_session.flush()

    # 4) Insert a Session row referencing the same guest
    session_obj = Session(
        session_id=SESSION_UUID,      # must match DB column for the sessions table
        guest_id=GUEST_UUID
    )
    async_session.add(session_obj)
    await async_session.commit()

    # 5) Provide them to the tests if needed
    yield (GUEST_UUID, SESSION_UUID)


# -------------------------
# Actual tests begin here
# -------------------------

@pytest.mark.asyncio
async def test_create_session_with_session_service(async_session, seed_guest_and_session):
    """
    'create_session' should return a SessionSchema for an existing guest.
    We'll re-use the GUEST_UUID from the fixture.
    """
    # Arrange
    service = SessionService(db=async_session)
    (GUEST_UUID, _) = seed_guest_and_session

    # Act
    new_session = await service.create_session(guest_id=GUEST_UUID)

    # Assert
    assert isinstance(new_session, SessionSchema)
    assert str(new_session.guest_id) == str(GUEST_UUID)
    assert new_session.session_id is not None


@pytest.mark.asyncio 
async def test_create_session_with_invalid_guest_id(async_session, seed_guest_and_session):
    """
    'create_session' should raise ValueError if the guest does not exist.
    """
    service = SessionService(db=async_session)
    # A random invalid UUID that won't match the seeded guest
    invalid_uuid = "99999999-9999-9999-9999-999999999999"

    with pytest.raises(ValueError):
        await service.create_session(guest_id=invalid_uuid)


@pytest.mark.asyncio 
async def test_get_session_from_session_id(async_session, seed_guest_and_session):
    """
    'get_session_from_session_id' should return a SessionSchema for the seeded session.
    """
    service = SessionService(db=async_session)
    (_, SESSION_UUID) = seed_guest_and_session

    sess = await service.get_session_from_session_id(session_id=SESSION_UUID)
    assert isinstance(sess, SessionSchema)
    assert str(sess.session_id) == str(SESSION_UUID)


@pytest.mark.asyncio
async def test_list_sessions_for_guest_id(async_session, seed_guest_and_session):
    """
    'list_sessions_for_guest_id' should return a list of SessionSchema 
    (including the seeded one).
    """
    service = SessionService(db=async_session)
    (GUEST_UUID, SESSION_UUID) = seed_guest_and_session

    sessions = await service.list_sessions_for_guest_id(guest_id=GUEST_UUID)
    assert isinstance(sessions, list)
    assert len(sessions) >= 1, "Expected at least one session for that guest"
    assert all(isinstance(s, SessionSchema) for s in sessions)
    
    # Compare as strings to avoid UUID vs string comparison issues
    session_ids = [str(s.session_id) for s in sessions]
    assert str(SESSION_UUID) in session_ids, "Seeded session should appear in the list"