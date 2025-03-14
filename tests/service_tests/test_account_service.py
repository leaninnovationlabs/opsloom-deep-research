import pytest
from uuid import UUID
from backend.api.account.services import AccountService
from backend.api.account.repository import AccountRepository
from backend.api.account.models import AccountCreate, AccountUpdate
from backend.lib.exceptions import AccountAlreadyExistsError, AccountNotFoundError

@pytest.mark.asyncio
async def test_create_account(async_session):
    """Test account creation through service layer"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="testserv",
        name="Service Test",
        email="service@test.com",
        protection="secret",
        metadata={"key": "value"}
    )
    
    # Act
    created_account = await service.create_account(account_data)
    
    # Assert
    assert created_account.account_id is not None
    assert created_account.short_code == "testserv"
    assert created_account.email == "service@test.com"
    assert created_account.metadata == {"key": "value"}
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_create_duplicate_account(async_session):
    """Test duplicate short code detection through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="duplicate",
        name="Original",
        email="original@test.com",
        protection="none"
    )
    created_account = await service.create_account(account_data)
    
    # Act & Assert
    with pytest.raises(AccountAlreadyExistsError):
        duplicate_data = AccountCreate(
            short_code="duplicate",
            name="Duplicate",
            email="duplicate@test.com",
            protection="none"
        )
        await service.create_account(duplicate_data)
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_get_account_by_id(async_session):
    """Test account retrieval by ID through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="getbyid",
        name="ID Lookup",
        email="idlookup@test.com",
        protection="none"
    )
    created_account = await service.create_account(account_data)
    
    # Act
    fetched_account = await service.get_account(created_account.account_id)
    
    # Assert
    assert fetched_account.account_id == created_account.account_id
    assert fetched_account.short_code == "getbyid"
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_get_account_by_short_code(async_session):
    """Test account retrieval by short code through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="shortcode",
        name="Short Code",
        email="short@test.com",
        protection="none"
    )
    created_account = await service.create_account(account_data)
    
    # Act
    fetched_account = await service.get_account_by_short_code("shortcode")
    
    # Assert
    assert fetched_account.short_code == "shortcode"
    assert fetched_account.email == "short@test.com"
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_get_account_config(async_session):
    """Test account config retrieval through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="configtest",
        name="Config Test",
        email="config@test.com",
        protection="none",
        metadata={"theme": "dark"}
    )
    created_account = await service.create_account(account_data)
    
    # Act
    config = await service.get_account_config_by_short_code("configtest")
    
    # Assert
    assert config.config == {"theme": "dark"}
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_get_root_account(async_session):
    """Test root account retrieval through service"""
    # Arrange & Act
    service = AccountService(AccountRepository(async_session))
    root_account = await service.get_root_account()
    
    # Assert
    assert root_account.short_code == "default"

@pytest.mark.asyncio
async def test_get_account_by_email(async_session):
    """Test account retrieval by email through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="emailtest",
        name="Email Test",
        email="emailtest@example.com",
        protection="none"
    )
    created_account = await service.create_account(account_data)
    
    # Act
    fetched_account = await service.get_account_by_email("emailtest@example.com")
    
    # Assert
    assert fetched_account.email == "emailtest@example.com"
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_update_account(async_session):
    """Test account update through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="beforeup",
        name="Before Update",
        email="before@test.com",
        protection="none"
    )
    created_account = await service.create_account(account_data)
    
    # Act
    update_data = AccountUpdate(
        account_id=created_account.account_id,
        short_code="afterup",
        name="After Update",
        email="after@test.com"
    )
    updated_account = await service.update_account(created_account.account_id, update_data)
    
    # Assert
    assert updated_account.short_code == "afterup"
    assert updated_account.name == "After Update"
    assert updated_account.email == "after@test.com"
    
    # Cleanup
    await repo.delete_account(created_account.account_id)

@pytest.mark.asyncio
async def test_validate_password(async_session):
    """Test password validation through service"""
    # Arrange
    repo = AccountRepository(async_session)
    service = AccountService(repo)
    account_data = AccountCreate(
        short_code="passval",
        name="Password Test",
        email="password@test.com",
        protection="secret123"
    )
    created_account = await service.create_account(account_data)
    
    # Act & Assert
    assert await service.validate_password("secret123") is True
    assert await service.validate_password("wrongpass") is False
    
    # Cleanup
    await repo.delete_account(created_account.account_id)