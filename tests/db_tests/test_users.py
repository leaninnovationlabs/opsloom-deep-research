import pytest
import pytest_asyncio
from uuid import uuid4
from random import randint 
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth.models import User
from backend.api.auth.repository import UserRepository
from backend.api.account.repository import AccountRepository
from backend.api.account.models import AccountCreate
from backend.api.account.account_schema import AccountORM
from backend.util.auth_utils import PasswordService

@pytest_asyncio.fixture(scope="function")
async def default_account(async_session: AsyncSession):
    """
    Create or retrieve a 'default' account for testing.
    """
    acct_repo = AccountRepository(async_session)

    # Attempt to retrieve the existing 'default' account
    default_acct = await acct_repo.get_account_by_short_code("default")
    if not default_acct:
        # If for some reason we don't have one, create it
        create_data = AccountCreate(
            short_code="default",
            name="Default Account",
            email="default@example.com",
            protection="email"  # or "none" or whatever you want
        )
        default_acct = await acct_repo.create_account(create_data)

    yield default_acct

    # Optionally clean up or do nothing. 
    # If your system requires 'default' to remain, skip deletion.
    # await async_session.delete(await async_session.merge(AccountORM(id=default_acct.id)))
    # await async_session.commit()

@pytest_asyncio.fixture(scope="function")
async def cleanup_users(async_session: AsyncSession):
    """
    Truncate the 'users' table before each test to ensure no data leaks.
    """
    # Before each test
    await async_session.execute("TRUNCATE TABLE users CASCADE;")
    await async_session.commit()

    yield

    # After each test (optional)
    await async_session.execute("TRUNCATE TABLE users CASCADE;")
    await async_session.commit()

@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession, default_account: AccountORM):
    """
    Test creating a user in the 'users' table with a hashed password.
    """
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()

    hashed = pw_service.hash_password("secret123")

    new_user = User(
        id=uuid4(),
        account_id=default_account.account_id,
        account_short_code="default",
        email="testuser@example.com",
        password=hashed,
        phone_no="123-456-7890",
        active=True
    )
    created = await user_repo.create_user(new_user)

    assert created is not None, "create_user(...) returned None"
    assert created.id is not None, "Expected user ID to be set"
    assert created.email == "testuser@example.com"
    assert created.account_short_code == "default"
    assert created.active is True

    # Now verify the password we stored actually matches "secret123"
    # We'll re-fetch from DB and do Argon2 verification
    retrieved = await user_repo.get_user_by_id(created.id)
    assert retrieved is not None
    # Argon2 verify
    assert pw_service.verify_password(retrieved.password, "secret123") is True

    # Clean up if desired
    await user_repo.delete_user(created.id)

@pytest.mark.asyncio
async def test_get_user_by_email(async_session: AsyncSession, default_account: AccountORM):
    """
    Test retrieving a user by their email address, verifying Argon2 hash works as expected.
    """
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()

    email = f"lookup{str(randint(1,100))}@example.com"
    hashed = pw_service.hash_password("lookup_pass")

    # Create the user
    user_data = User(
        id=uuid4(),
        account_id=default_account.account_id,
        account_short_code="default",
        email=email,
        password=hashed,
        phone_no="123-456-7890",
        active=True
    )
    test_user = await user_repo.create_user(user_data)

    # Now look it up
    found = await user_repo.get_user_by_email(test_user.email)
    assert found is not None, "Expected to find a user by email"
    assert found.email == email
    assert found.account_id == default_account.account_id

    # Confirm we can verify the password
    assert pw_service.verify_password(found.password, "lookup_pass") is True

    await user_repo.delete_user(found.id)

@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession, default_account: AccountORM):
    """
    Test retrieving a user by UUID, verifying the password via Argon2.
    """
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()

    new_id = uuid4()
    hashed = pw_service.hash_password("mysecret")

    # Create a user
    user_data = User(
        id=new_id,
        account_id=default_account.account_id,
        account_short_code="default",
        email="byid@example.com",
        password=hashed,
        phone_no="123-456-7890",
        active=True
    )
    created = await user_repo.create_user(user_data)
    assert created is not None

    # Lookup by ID
    fetched = await user_repo.get_user_by_id(new_id)
    assert fetched is not None, "get_user_by_id returned None"
    assert fetched.id == new_id
    assert fetched.email == "byid@example.com"

    # Check password
    assert pw_service.verify_password(fetched.password, "mysecret")

    await user_repo.delete_user(new_id)

@pytest.mark.asyncio
async def test_update_user(async_session: AsyncSession, default_account: AccountORM):
    """
    Test updating an existing user, ensuring Argon2 hashing is preserved.
    """
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()

    # 1) Create a user with an initial hash
    original_hashed = pw_service.hash_password("oldpass")
    user_data = User(
        id=uuid4(),
        account_id=default_account.account_id,
        account_short_code="default",
        email="update_me@example.com",
        password=original_hashed,
        phone_no="123-456-7890",
        active=True
    )
    created = await user_repo.create_user(user_data)
    assert created is not None

    # 2) We want to update the password => produce a new Argon2 hash
    new_hashed = pw_service.hash_password("newpass")
    created.email = "updated@example.com"
    created.password = new_hashed
    created.active = False

    updated_user = await user_repo.update_user(created)
    assert updated_user is not None, "Expected update_user to return a user"
    assert updated_user.email == "updated@example.com"
    assert updated_user.active is False

    # Finally, confirm the new Argon2 hash verifies "newpass"
    assert pw_service.verify_password(updated_user.password, "newpass"), (
        "The updated user's password should match 'newpass'"
    )

    # Also confirm it does NOT verify the old password
    assert not pw_service.verify_password(updated_user.password, "oldpass"), (
        "The updated user's password should *not* match 'oldpass'"
    )

    await user_repo.delete_user(updated_user.id)
