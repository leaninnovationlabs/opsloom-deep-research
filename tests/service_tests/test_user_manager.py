import pytest
from uuid import UUID
from backend.api.auth.session import UserManager
from backend.api.auth.repository import UserRepository
from backend.api.account.services import AccountService
from backend.api.account.models import AccountCreate
from backend.api.auth.models import User
from backend.api.account.repository import AccountRepository
from backend.api.auth.models import UserLogin, UserCreate
from backend.util.auth_utils import PasswordService
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_successful_login(async_session: AsyncSession):
    """Test successful user login with valid credentials"""
    # Arrange
    user_repo = UserRepository(async_session)
    account_repo = AccountRepository(async_session)
    account_service = AccountService(account_repo)
    manager = UserManager(user_repo, account_service)
    pw_service = PasswordService()

    # Create test account
    test_account = await account_repo.create_account(
        AccountCreate(
            short_code="test_login",
            name="Test Login Account",
            email="login@test.com",
            protection="email"
        )
    )

    # Create test user
    test_user = await user_repo.create_user(
        User(
            email="user@test.com",
            account_id=test_account.account_id,
            account_short_code="test_login",
            password=pw_service.hash_password("validpass"),
            active=True
        )
    )

    # Act
    login_request = UserLogin(
        email="user@test.com",
        password="validpass",
        account_short_code="test_login"
    )
    token, message, user = await manager.login_user(login_request)

    assert user.email == "user@test.com"
    assert message == "Logged in successfully"

    # Cleanup
    await user_repo.delete_user(test_user.id)
    await account_repo.delete_account(test_account.account_id)

@pytest.mark.asyncio
async def test_invalid_password_login(async_session: AsyncSession):
    """Test login with invalid password"""
    # Arrange
    user_repo = UserRepository(async_session)
    account_service = AccountService(AccountRepository(async_session))
    manager = UserManager(user_repo, account_service)
    
    # Create test data
    test_user = await user_repo.create_user(
        User(
            email="invalidpass@test.com",
            account_id=(await account_service.get_root_account()).account_id,
            account_short_code="default",
            password=PasswordService().hash_password("correctpass"),
            active=True
        )
    )

    # Act
    login_request = UserLogin(
        email="invalidpass@test.com",
        password="wrongpass",
        account_short_code="default"
    )
    token, message, user = await manager.login_user(login_request)

    # Assert
    assert token is None
    assert user is None
    assert "Invalid credentials" in message

    # Cleanup
    await user_repo.delete_user(test_user.id)

@pytest.mark.asyncio
async def test_signup_email_protected(async_session: AsyncSession):
    """Test successful signup for email-protected account"""
    # Arrange
    user_repo = UserRepository(async_session)
    account_repo = AccountRepository(async_session)
    account_service = AccountService(account_repo)
    manager = UserManager(user_repo, account_service)

    # Create protected account
    protected_account = await account_repo.create_account(
        AccountCreate(
            short_code="protected",
            name="Protected Account",
            email="protected@test.com",
            protection="email"
        )
    )

    # Act
    signup_request = UserCreate(
        account_shortcode="protected",
        email="newuser@test.com",
        password="ValidPassword123!",
        phone_no="123-456-7890"
    )
    token, message, user = await manager.signup_user(signup_request)

    # Assert
    assert token is not None
    assert user is not None
    assert user.email == "newuser@test.com"
    assert "created and logged in" in message

    # Cleanup
    created_user = await user_repo.get_user_by_email("newuser@test.com")
    if created_user:
        await user_repo.delete_user(created_user.id)
    await account_repo.delete_account(protected_account.account_id)


@pytest.mark.asyncio
async def test_signup_existing_user(async_session: AsyncSession):
    """Test signup with already registered email"""
    # Arrange
    user_repo = UserRepository(async_session)
    account_service = AccountService(AccountRepository(async_session))
    manager = UserManager(user_repo, account_service)
    
    # Create existing user
    existing_user = await user_repo.create_user(
        User(
            email="exists@test.com",
            account_id=(await account_service.get_root_account()).account_id,
            account_short_code="default",
            password=PasswordService().hash_password("existingpass"),
            active=True
        )
    )

    # Act
    signup_request = UserCreate(
        account_shortcode="default",
        email="exists@test.com",
        password="newpass123",
        phone_no="123-456-7890"
    )
    token, message, user = await manager.signup_user(signup_request)

    # Assert
    assert token is None
    assert "internal server error" in message.lower()

    # Cleanup
    await user_repo.delete_user(existing_user.id)