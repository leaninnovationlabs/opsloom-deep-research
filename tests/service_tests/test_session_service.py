import pytest
import pytest_asyncio
import uuid
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

# Service and Models
from backend.api.session.services import SessionService
from backend.api.session.models import UserSession
from backend.util.auth_utils import TokenData, PasswordService

# Repositories and Models for fixture setup
from backend.api.auth.repository import UserRepository
from backend.api.account.repository import AccountRepository
from backend.api.assistant.repository import AssistantRepository
from backend.api.kbase.repository import KbaseRepository
from backend.api.auth.models import User
from backend.api.account.models import AccountCreate
from backend.api.kbase.models import KnowledgeBase
from backend.api.assistant.models import Assistant, AssistantConfig, Metadata

@pytest_asyncio.fixture(scope="function")
async def service_dependencies(async_session: AsyncSession):
    """Fixture to set up user and assistant dependencies for session service tests"""
    # 1) Ensure root account exists
    acct_repo = AccountRepository(async_session)
    root_acct = await acct_repo.get_root_account()
    if not root_acct:
        fallback = AccountCreate(
            short_code="rootuser",
            name="Root ServiceTest",
            email="root@service.test",
            protection="none",
        )
        root_acct = await acct_repo.create_account(fallback)
        await async_session.execute(
            "UPDATE account SET root = TRUE WHERE id = :rid",
            {"rid": str(root_acct.account_id)},
        )
        await async_session.commit()

    # 2) Create test user
    user_repo = UserRepository(async_session)
    hashed_pw = PasswordService().hash_password("svc_test_pass")
    new_user = User(
        id=uuid4(),
        account_id=root_acct.account_id,
        account_short_code=root_acct.short_code,
        email="session_service_user@test.com",
        password=hashed_pw,
        phone_no="555-555-9876",
        active=True
    )
    created_user = await user_repo.create_user(new_user)

    # 3) Create knowledge base
    kbase_repo = KbaseRepository(async_session)
    unique_suffix = str(uuid.uuid4())[:8]
    kb_data = KnowledgeBase(
        name=f"svc_test_kb_{unique_suffix}",
        description="Service Test KB",
        account_short_code=root_acct.short_code
    )
    created_kb = await kbase_repo.create_kbase(kb_data)

    # 4) Create assistant
    assistant_repo = AssistantRepository(async_session)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4")
    a_in = Assistant(
        account_short_code=root_acct.short_code,
        kbase_id=created_kb.id,
        name=f"SvcTestAsst_{unique_suffix}",
        config=config,
        system_prompts={},
        assistant_metadata=Metadata(
            title="Service Test Assistant",
            description="For service-level testing",
            icon="test_icon.png",
            prompts=[],
            num_history_messages=0
        )
    )
    created_asst = await assistant_repo.create_assistant(a_in)

    yield (created_user, created_asst)

    # Cleanup
    await assistant_repo.delete_assistant(str(created_asst.id))
    await user_repo.delete_user(created_user.id)
    await kbase_repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_create_session_object(async_session: AsyncSession, service_dependencies):
    """Test creating a session object without persistence"""
    # Arrange
    user, assistant = service_dependencies
    curr_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,  # Added missing field
        email=user.email,
        scopes=[]
    )
    service = SessionService(async_session)

    # Act
    session_obj = await service.create_session_object(curr_user, assistant.id)

    # Assert
    assert session_obj is not None
    assert isinstance(session_obj, UserSession)
    assert session_obj.user_id == user.id
    assert session_obj.account_id == user.account_id
    assert session_obj.assistant_id == assistant.id
    assert session_obj.title == ""

@pytest.mark.asyncio
async def test_store_and_retrieve_session(async_session: AsyncSession, service_dependencies):
    """Test storing and retrieving a session"""
    # Arrange
    user, assistant = service_dependencies
    curr_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,  # Added missing field
        email=user.email,
        scopes=[]
    )
    service = SessionService(async_session)
    session_obj = await service.create_session_object(curr_user, assistant.id)
    session_obj.title = "Test Storage Session"
    session_obj.data = {"test": "data"}

    # Act - Store
    stored_session = await service.store_chat_session(session_obj)

    try:
        # Assert Storage
        assert stored_session.id is not None
        assert stored_session.title == "Test Storage Session"

        # Act - Retrieve
        fetched_session = await service.get_session(stored_session.id)

        # Assert Retrieval
        assert fetched_session is not None
        assert fetched_session.id == stored_session.id
        assert fetched_session.data == {"test": "data"}
    finally:
        # Cleanup
        await service.delete_session(stored_session.id)

@pytest.mark.asyncio
async def test_update_session_title(async_session: AsyncSession, service_dependencies):
    """Test updating a session title"""
    # Arrange
    user, assistant = service_dependencies
    curr_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,  # Added missing field
        email=user.email,
        scopes=[]
    )
    service = SessionService(async_session)
    session_obj = await service.create_session_object(curr_user, assistant.id)
    stored_session = await service.store_chat_session(session_obj)
    new_title = "Updated Title"

    try:
        # Act
        update_success = await service.update_session_title(stored_session.id, new_title)
        
        # Assert
        assert update_success is True
        
        # Verify
        updated_session = await service.get_session(stored_session.id)
        assert updated_session.title == new_title
    finally:
        # Cleanup
        await service.delete_session(stored_session.id)

@pytest.mark.asyncio
async def test_delete_session(async_session: AsyncSession, service_dependencies):
    """Test session deletion"""
    # Arrange
    user, assistant = service_dependencies
    curr_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,  # Added missing field
        email=user.email,
        scopes=[]
    )
    service = SessionService(async_session)
    session_obj = await service.create_session_object(curr_user, assistant.id)
    stored_session = await service.store_chat_session(session_obj)

    # Act
    delete_success = await service.delete_session(stored_session.id)

    # Assert
    assert delete_success is True
    deleted_session = await service.get_session(stored_session.id)
    assert deleted_session is None

@pytest.mark.asyncio
async def test_list_user_sessions(async_session: AsyncSession, service_dependencies):
    """Test listing user sessions"""
    # Arrange
    user, assistant = service_dependencies
    curr_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,  # Added missing field
        email=user.email,
        scopes=[]
    )
    service = SessionService(async_session)

    # Create multiple sessions
    session1 = await service.create_session_object(curr_user, assistant.id)
    session1.title = "First Session"
    stored1 = await service.store_chat_session(session1)

    session2 = await service.create_session_object(curr_user, assistant.id)
    session2.title = "Second Session"
    stored2 = await service.store_chat_session(session2)

    try:
        # Act
        session_list = await service.list_sessions(user.id)

        # Assert
        assert len(session_list.list) >= 2
        titles = [sess.title for sess in session_list.list]
        assert "First Session" in titles
        assert "Second Session" in titles
    finally:
        # Cleanup
        await service.delete_session(stored1.id)
        await service.delete_session(stored2.id)