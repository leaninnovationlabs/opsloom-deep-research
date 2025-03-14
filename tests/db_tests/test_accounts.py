import pytest
import uuid
from backend.api.account.repository import AccountRepository
from backend.api.account.models import AccountCreate, AccountUpdate
from backend.api.account.account_schema import AccountORM
from backend.lib.exceptions import (
    AccountAlreadyExistsError,
    AccountNotFoundError
)

@pytest.mark.asyncio
async def test_create_account(async_session):
    repo = AccountRepository(async_session)
    account_data = AccountCreate(
        short_code="test_short",
        name="Test Account",
        email="test@example.com",
        protection="password",
        metadata={"color": "blue"}
    )
    account = None
    try:
        account = await repo.create_account(account_data)
        assert account.account_id is not None
        assert account.short_code == "test_short"
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_create_account_unique_short_code(async_session):
    repo = AccountRepository(async_session)
    acct1 = None
    try:
        account_data_1 = AccountCreate(
            short_code="uniquecode",
            name="Account 1",
            email="unique1@example.com",
            protection="none"
        )
        acct1 = await repo.create_account(account_data_1)

        with pytest.raises(AccountAlreadyExistsError):
            account_data_2 = AccountCreate(
                short_code="uniquecode",
                name="Account 2",
                email="unique2@example.com",
                protection="none"
            )
            await repo.create_account(account_data_2)
    finally:
        if acct1:
            await repo.delete_account(acct1.account_id)

@pytest.mark.asyncio
async def test_get_account_by_id(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="by_id",
            name="Lookup Name",
            email="lookup@example.com",
            protection="none"
        )
        account = await repo.create_account(acct_create)
        fetched_acct = await repo.get_account_by_id(account.account_id)
        assert fetched_acct.account_id == account.account_id
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_get_account_by_short_code(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="myshort",
            name="ShortCodeUser",
            email="shortcode@example.com",
            protection="none"
        )
        account = await repo.create_account(acct_create)
        fetched_acct = await repo.get_account_by_short_code("myshort")
        assert fetched_acct.short_code == "myshort"
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_get_account_config_by_short_code(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="configtest",
            name="Config Tester",
            email="config@example.com",
            protection="none",
            metadata={"theme": "dark"}
        )
        account = await repo.create_account(acct_create)
        config = await repo.get_account_config_by_short_code("configtest")
        assert config.config == {"theme": "dark"}
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_get_root_account(async_session):
    repo = AccountRepository(async_session)
    root_acct = await repo.get_root_account()
    assert root_acct.short_code == "default"


@pytest.mark.asyncio
async def test_get_account_by_email(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="emailtest",
            name="EmailTest Name",
            email="emailtest@example.com",
            protection="none"
        )
        account = await repo.create_account(acct_create)
        found_acct = await repo.get_account_by_email("emailtest@example.com")
        assert found_acct is not None
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_verify_email(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="emailverif",
            name="EmailVerify",
            email="verify@example.com",
            protection="none"
        )
        account = await repo.create_account(acct_create)
        assert await repo.verify_email("verify@example.com") is True
        assert await repo.verify_email("bogus@example.com") is False
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_validate_password(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="passcheck",
            name="Password Check",
            email="pass@example.com",
            protection="mysecret"
        )
        account = await repo.create_account(acct_create)
        assert await repo.validate_password("mysecret") is True
        assert await repo.validate_password("wrongsecret") is False
    finally:
        if account:
            await repo.delete_account(account.account_id)

@pytest.mark.asyncio
async def test_update_account(async_session):
    repo = AccountRepository(async_session)
    account = None
    try:
        acct_create = AccountCreate(
            short_code="updateme",
            name="Update Me",
            email="update@example.com",
            protection="none"
        )
        account = await repo.create_account(acct_create)
        update_data = AccountUpdate(
            account_id=account.account_id,
            short_code="updated",
            name="Updated Name",
            email="updated@example.com",
        )
        updated_acct = await repo.update_account(update_data)
        assert updated_acct.short_code == "updated"
    finally:
        if account:
            await repo.delete_account(account.account_id)