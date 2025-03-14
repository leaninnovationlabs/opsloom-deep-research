import pytest
import pytest_asyncio
import uuid
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

# Repositories
from backend.api.session.repository import SessionRepository
from backend.api.auth.repository import UserRepository
from backend.api.account.repository import AccountRepository
from backend.api.assistant.repository import AssistantRepository
from backend.api.kbase.repository import KbaseRepository

# Models
from backend.api.session.models import UserSession, SessionList
from backend.api.auth.models import User
from backend.api.assistant.models import Assistant, AssistantConfig, Metadata
from backend.api.kbase.models import KnowledgeBase

# Utils
from backend.util.auth_utils import PasswordService


@pytest_asyncio.fixture(scope="function")
async def session_dependencies(async_session: AsyncSession):
    """
    Fixture that sets up:
      1) Root Account (if not already existing)
      2) A new User referencing that root account
      3) A new KnowledgeBase
      4) A new Assistant referencing that KB
    Yields (user, assistant).
    Cleans up after each test (deletes user, assistant, KB).
    """

    # 1) Ensure we have a root account
    acct_repo = AccountRepository(async_session)
    root_acct = await acct_repo.get_root_account()
    # If for some reason there's no root account, you could create one here
    if not root_acct:
        # Minimal fallback root account
        from backend.api.account.models import AccountCreate
        fallback = AccountCreate(
            short_code="rootuser",
            name="Root Name",
            email="root@root.com",
            protection="none",
        )
        root_acct = await acct_repo.create_account(fallback)
        # Mark it as root
        await async_session.execute(
            "UPDATE account SET root = TRUE WHERE id = :rid",
            {"rid": str(root_acct.account_id)},
        )
        await async_session.commit()

    # 2) Create a user referencing the root account
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()
    hashed_pw = pw_service.hash_password("sessiontestpass")
    new_user = User(
        id=uuid4(),
        account_id=root_acct.account_id,
        account_short_code=root_acct.short_code,
        email="session_user@example.com",
        password=hashed_pw,
        phone_no="555-555-1234",
        active=True
    )
    created_user = await user_repo.create_user(new_user)

    # 3) Create a minimal knowledge base, for the assistant
    kbase_repo = KbaseRepository(async_session)
    unique_suffix = str(uuid.uuid4())[:8]
    kb_data = KnowledgeBase(
        name=f"test_kbase_{unique_suffix}",
        description="KB for session tests",
        account_short_code=root_acct.short_code
    )
    created_kb = await kbase_repo.create_kbase(kb_data)

    # 4) Create an Assistant referencing the KB
    assistant_repo = AssistantRepository(async_session)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code=root_acct.short_code,
        kbase_id=created_kb.id,
        name=f"SessionTestAssistant_{unique_suffix}",
        config=config,
        system_prompts={},
        assistant_metadata=Metadata(
            title="SessionTest Assistant",
            description="Assistant for session tests",
            icon="test_icon.png",
            prompts=[],
            num_history_messages=0
        )
    )
    created_asst = await assistant_repo.create_assistant(a_in)

    # Yield the user + assistant
    yield (created_user, created_asst)

    # Cleanup: delete the assistant, the user, and the KB
    await assistant_repo.delete_assistant(str(created_asst.id))
    await user_repo.delete_user(created_user.id)
    await kbase_repo.delete_kbase(created_kb.id)


@pytest.mark.asyncio
async def test_create_session(async_session: AsyncSession, session_dependencies):
    """
    Test creating a new user session in the DB, referencing user + assistant from fixture.
    """
    user, assistant = session_dependencies
    repo = SessionRepository(async_session)

    session_data = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="My Test Session",
        data={"foo": "bar"}
    )

    created = await repo.set_user_session(session_data)
    assert created is not None, "Creating session returned None"
    assert created.id is not None, "Expected newly created session to have an ID"
    assert created.title == "My Test Session"
    assert created.data == {"foo": "bar"}

    # Clean up: delete the session
    deleted = await repo.delete_user_session(created.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_get_user_session(async_session: AsyncSession, session_dependencies):
    """
    Test retrieving a session by its UUID.
    """
    user, assistant = session_dependencies
    repo = SessionRepository(async_session)

    session_data = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="SessionForGet",
        data={"hello": "world"}
    )
    created = await repo.set_user_session(session_data)
    assert created is not None

    # Now retrieve it
    fetched = await repo.get_user_session(created.id)
    assert fetched is not None, "Fetching session by ID returned None"
    assert fetched.id == created.id
    assert fetched.title == "SessionForGet"
    assert fetched.data == {"hello": "world"}

    # Clean up
    deleted = await repo.delete_user_session(created.id)
    assert deleted is True


@pytest.mark.asyncio
async def test_update_session_title(async_session: AsyncSession, session_dependencies):
    """
    Test updating the session title for an existing record.
    """
    user, assistant = session_dependencies
    repo = SessionRepository(async_session)

    session_data = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="Old Title"
    )
    created = await repo.set_user_session(session_data)
    assert created, "Failed to create initial session"

    # Update the title
    new_title = "New Session Title"
    updated = await repo.update_session_title(created.id, new_title)
    assert updated is True, "Expected update_session_title(...) to return True"

    # Retrieve again, confirm new title
    fetched = await repo.get_user_session(created.id)
    assert fetched is not None
    assert fetched.title == new_title

    # Clean up
    await repo.delete_user_session(created.id)


@pytest.mark.asyncio
async def test_list_user_sessions(async_session: AsyncSession, session_dependencies):
    """
    Test listing sessions for a particular user_id.
    """
    user, assistant = session_dependencies
    repo = SessionRepository(async_session)

    # Create two sessions for the same user
    s1 = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="UserSessionOne"
    )
    s2 = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="UserSessionTwo"
    )
    created_1 = await repo.set_user_session(s1)
    created_2 = await repo.set_user_session(s2)

    # Now list sessions by the original user's ID
    session_list = await repo.list_user_sessions(user.id)
    assert len(session_list.list) >= 2, "Expected at least 2 sessions for user"
    titles = [sess.title for sess in session_list.list]
    assert "UserSessionOne" in titles
    assert "UserSessionTwo" in titles

    # Clean up
    await repo.delete_user_session(created_1.id)
    await repo.delete_user_session(created_2.id)


@pytest.mark.asyncio
async def test_delete_session(async_session: AsyncSession, session_dependencies):
    """
    Test deleting a user session by its ID.
    """
    user, assistant = session_dependencies
    repo = SessionRepository(async_session)

    s_data = UserSession(
        user_id=user.id,
        account_id=user.account_id,
        assistant_id=assistant.id,
        title="ToDelete"
    )
    created = await repo.set_user_session(s_data)
    assert created is not None

    # Delete it
    deleted = await repo.delete_user_session(created.id)
    assert deleted is True, "delete_user_session(...) returned False"

    # Confirm it's gone
    fetched = await repo.get_user_session(created.id)
    assert fetched is None, "Expected the session to be gone after deletion"
