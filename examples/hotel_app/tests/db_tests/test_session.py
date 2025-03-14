import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.db.models import Guest, Session
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID, uuid4
from backend.schemas.session import SessionSchema
from backend.db.repositories.session import SessionRepository


@pytest_asyncio.fixture
async def seed_guest_and_session(async_session: AsyncSession):
    """
    Clear relevant tables and seed a known guest + session for SQLite.
    """
    # SQLite doesn't support TRUNCATE, use DELETE instead
    await async_session.execute(text("DELETE FROM reservations"))
    await async_session.execute(text("DELETE FROM sessions"))
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()

    GUEST_UUID = "12345678-1234-5678-1234-567812345678"
    SESSION_UUID = "87654321-4321-8765-4321-567812345678"

    # Insert the guest
    new_guest = Guest(
        guest_id=GUEST_UUID,
        full_name="Test Guest",
        email="test.guest@example.com",
    )
    async_session.add(new_guest)

    # Insert a session referencing that same guest
    new_session = Session(
        session_id=SESSION_UUID,
        guest_id=GUEST_UUID,
    )
    async_session.add(new_session)

    await async_session.commit()

    return (GUEST_UUID, SESSION_UUID)


@pytest.mark.asyncio
async def test_list_sessions_returns_list_of_session_schema(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'list_sessions' returns a non-empty list
    """
    repo = SessionRepository(db=async_session)
    sessions = await repo.list_sessions()
    assert len(sessions) > 0, "Expected at least one session in DB"
    assert isinstance(sessions[0], SessionSchema), "Expected session to be SessionSchema instance"


@pytest.mark.asyncio
async def test_add_session_returns_session_schema(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'add_session' returns a SessionSchema,
    referencing an existing guest so we don't get FK errors.
    """
    repo = SessionRepository(db=async_session)
    # We seeded a guest with ID=1234... so let's re-use that
    guest_uuid = seed_guest_and_session[0]
    session_uuid = str(uuid.uuid4())  # Convert to string for SQLite

    new_session = SessionSchema(
        session_id=session_uuid,
        guest_id=guest_uuid,
    )
    added_session = await repo.add_session(new_session)

    assert isinstance(added_session, SessionSchema)
    assert str(added_session.session_id) == str(session_uuid), "Session IDs should match as strings"
    assert str(added_session.guest_id) == str(guest_uuid), "Guest IDs should match as strings"


@pytest.mark.asyncio
async def test_get_session_by_id_returns_session_schema(async_session: AsyncSession, seed_guest_and_session):
    """
    We seeded a session with session_id=8765... so let's retrieve it
    """
    repo = SessionRepository(db=async_session)
    test_session_id = seed_guest_and_session[1]  # 87654321-4321-...

    session = await repo.get_session_by_id(test_session_id)
    assert session is not None
    assert str(session.session_id) == str(test_session_id), "Session IDs should match as strings"
    assert isinstance(session, SessionSchema)


@pytest.mark.asyncio
async def test_get_sessions_by_guest_id_returns_session_schema(async_session: AsyncSession, seed_guest_and_session):
    repo = SessionRepository(db=async_session)
    test_guest_id = seed_guest_and_session[0]

    sessions = await repo.get_sessions_by_guest_id(test_guest_id)
    assert len(sessions) >= 1, "Expected at least one session for the seeded guest"
    for s in sessions:
        assert str(s.guest_id) == str(test_guest_id), "Guest IDs should match as strings"
        assert isinstance(s, SessionSchema)


@pytest.mark.asyncio
async def test_delete_sessions_returns_bool(async_session: AsyncSession, seed_guest_and_session):
    repo = SessionRepository(db=async_session)
    # We'll remove sessions for that seeded guest
    test_guest_id = seed_guest_and_session[0]

    result = await repo.delete_sessions(test_guest_id)
    assert result is True, "Expected True if sessions were deleted"

    leftover = await repo.get_sessions_by_guest_id(test_guest_id)
    assert len(leftover) == 0, "Expected no sessions left for that guest"