import pytest
import uuid 
from sqlalchemy.ext.asyncio import AsyncSession

from backend.schemas.message import MessagePairSchema, MessageSchema
from backend.db.repositories.message import MessageRepository

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.db.models import Guest, Session

@pytest_asyncio.fixture
async def seed_guest_and_session(async_session: AsyncSession):
    # SQLite doesn't support TRUNCATE, use DELETE instead
    await async_session.execute(text("DELETE FROM reservations"))
    await async_session.execute(text("DELETE FROM messages"))
    await async_session.execute(text("DELETE FROM sessions"))
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()

    # Now insert your new Guest / Session
    GUEST_UUID = "12345678-1234-5678-1234-567812345678"
    SESSION_UUID = "87654321-4321-8765-4321-567812345678"

    new_guest = Guest(
        guest_id=GUEST_UUID,
        full_name="Test Guest",
        email="test.guest@example.com"
    )
    new_session = Session(
        session_id=SESSION_UUID,
        guest_id=GUEST_UUID,
    )

    async_session.add(new_guest)
    async_session.add(new_session)
    await async_session.commit()

    return (GUEST_UUID, SESSION_UUID)


@pytest.mark.asyncio
async def test_add_message_returns_message_pair_schema(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'add_message' in 'MessageRepository' returns
    a MessagePairSchema object after adding a new message pair.
    """
    # Thanks to the fixture, we have a real Guest & Session with known UUIDs
    guest_id, session_id = seed_guest_and_session

    repo = MessageRepository(db=async_session)

    new_message_pair = MessagePairSchema(
        guest_id=guest_id,
        session_id=session_id,
        user_message=MessageSchema(
            content="Hello from the user!",
            role="user"
        ),
        ai_message=MessageSchema(
            content="Hi there, I'm the AI.",
            role="assistant"
        )
    )

    # Act
    added_message_pair = await repo.add_message(new_message_pair)

    # Compare as strings to handle UUID vs string comparisons
    assert isinstance(added_message_pair, MessagePairSchema)
    assert str(added_message_pair.guest_id) == str(guest_id), "Guest ID should match"
    assert str(added_message_pair.session_id) == str(session_id), "Session ID should match"
    assert added_message_pair.user_message.content == "Hello from the user!"
    assert added_message_pair.ai_message.content == "Hi there, I'm the AI."


@pytest.mark.asyncio
async def test_list_messages_returns_list_of_message_pairs(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'list_messages' in 'MessageRepository' returns
    a list of MessagePairSchema objects.
    """
    guest_id, session_id = seed_guest_and_session
    repo = MessageRepository(db=async_session)

    # Possibly insert one message first so that list_messages() won't be empty
    new_msg = MessagePairSchema(
        guest_id=guest_id,
        session_id=session_id,
        user_message=MessageSchema(content="Hi from user", role="user"),
        ai_message=MessageSchema(content="Hello back", role="assistant"),
    )
    await repo.add_message(new_msg)

    # Act
    messages = await repo.list_messages()

    # Assert
    assert len(messages) >= 1, "Expected at least one message in the DB"


@pytest.mark.asyncio
async def test_get_messages_by_session_id(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'get_messages_by_session_id' returns
    MessagePairSchema objects for a given session.
    """
    guest_id, session_id = seed_guest_and_session
    repo = MessageRepository(db=async_session)

    # Insert a message for that session
    new_msg = MessagePairSchema(
        guest_id=guest_id,
        session_id=session_id,
        user_message=MessageSchema(content="Session-based user msg", role="user"),
        ai_message=MessageSchema(content="Session-based AI msg", role="assistant"),
    )
    await repo.add_message(new_msg)

    # Act
    messages = await repo.get_messages_by_session_id(session_id)

    # Assert
    assert len(messages) >= 1, "Expected at least one message for this session"
    for msg in messages:
        assert str(msg.session_id) == str(session_id), "Session IDs should match"


@pytest.mark.asyncio
async def test_delete_messages_by_session_id(async_session: AsyncSession, seed_guest_and_session):
    """
    Tests that 'delete_messages_by_session_id' returns
    a boolean indicating successful deletion of messages for a session.
    """
    guest_id, session_id = seed_guest_and_session
    repo = MessageRepository(db=async_session)

    # Insert a message
    new_msg = MessagePairSchema(
        guest_id=guest_id,
        session_id=session_id,
        user_message=MessageSchema(content="I'll be deleted", role="user"),
        ai_message=MessageSchema(content="So will I", role="assistant"),
    )
    await repo.add_message(new_msg)

    # Act
    result = await repo.delete_messages_by_session_id(session_id)

    # If your repo returns True, great
    assert result is True, "Expected messages to be deleted for that session"

    leftover = await repo.get_messages_by_session_id(session_id)
    assert len(leftover) == 0, "Expected all messages for that session to be removed"