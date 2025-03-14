import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from sqlalchemy import text
from backend.db.repositories.guest import GuestRepository
from backend.schemas.guest import GuestSchema
from backend.db.models import Guest

@pytest_asyncio.fixture
async def seed_test_guest(async_session: AsyncSession):
    """Seed a known test guest for our tests"""
    # Clean the guests table to ensure we have a clean state
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()
    
    # Create a test guest directly in the database
    test_guest = Guest(
        guest_id="12345678-1234-5678-1234-567812345678",
        full_name="Peter Griffin",
        email="peter.griffin@quahog.com",
        phone="(715) 555-0101"
    )
    async_session.add(test_guest)
    await async_session.commit()
    
    return test_guest.guest_id

@pytest.mark.asyncio
async def test_list_guests_returns_list_of_guest_schema(async_session: AsyncSession, seed_test_guest):
    """
    Tests that 'list_guests' in 'GuestRepository' returns
    a non-empty list of GuestSchema objects from our seeded database.
    """
    # Arrange
    repo = GuestRepository(db=async_session)

    # Act
    guests = await repo.list_guests()

    # Assert
    assert len(guests) > 0, "Expected at least one guest to be returned"
    assert isinstance(guests[0], GuestSchema), "Expected item to be an instance of GuestSchema"

@pytest.mark.asyncio
async def test_get_guest_by_email_returns_guest_schema(async_session: AsyncSession, seed_test_guest):
    """
    Tests that 'get_guest_by_email' in 'GuestRepository' returns
    a GuestSchema object for a given email from our seeded database.
    """
    # Arrange
    repo = GuestRepository(db=async_session)
    # Using one of the emails from our seed data - change if you modified the email format
    test_email = "peter.griffin@quahog.com"

    # Act
    guest = await repo.get_guest_by_email(email=test_email)

    # Assert
    assert guest.email == test_email, "Expected guest email to match the test email"

@pytest.mark.asyncio
async def test_create_guest_returns_guest_schema(async_session: AsyncSession):
    """
    Tests that 'create_guest' in 'GuestRepository' returns
    a GuestSchema object for a new guest.
    """
    # Arrange
    repo = GuestRepository(db=async_session)
    test_guest = GuestSchema(
        full_name="Test Guest",
        email="test123@email.org",
        phone="1234567890"
    )

    # Act
    guest = await repo.create_guest(guest=test_guest)

    # Assert
    assert guest.email == test_guest.email, "Expected guest email to match the test email"
    assert guest.full_name == test_guest.full_name, "Expected guest full name to match the test full name"
    assert guest.guest_id is not None, "Expected guest_id to be assigned"

@pytest.mark.asyncio
async def test_get_guest_by_id_returns_guest_schema(async_session: AsyncSession):
    """
    Tests that 'get_guest_by_id' in 'GuestRepository' returns
    a GuestSchema object for a given ID.
    """
    # Arrange - First create a guest to get an ID
    repo = GuestRepository(db=async_session)
    test_guest = GuestSchema(
        full_name="Test ID Guest",
        email="id_test@email.org",
        phone="9876543210"
    )
    created_guest = await repo.create_guest(guest=test_guest)
    
    # Act
    guest = await repo.get_guest_by_id(guest_id=created_guest.guest_id)
    
    # Assert
    assert guest is not None, "Expected to find a guest with that ID"
    assert str(guest.guest_id) == str(created_guest.guest_id), "Expected guest ID to match"
    assert guest.email == test_guest.email, "Expected email to match"

@pytest.mark.asyncio
async def test_delete_guest_deletes_guest(async_session: AsyncSession):
    """
    Tests that 'delete_guest' in 'GuestRepository' deletes
    a guest from the database.
    """
    # Arrange - First create a guest to then delete
    repo = GuestRepository(db=async_session)
    test_email = f"delete_test_{uuid.uuid4()}@email.org"
    test_guest = GuestSchema(
        full_name="Delete Test Guest",
        email=test_email
    )
    await repo.create_guest(guest=test_guest)
    
    # Act
    result = await repo.delete_guest(email=test_email)
    
    # Assert
    assert result is True, "Expected True to indicate successful deletion"
    
    # Try to find the deleted guest
    with pytest.raises(ValueError):
        await repo.get_guest_by_email(email=test_email)