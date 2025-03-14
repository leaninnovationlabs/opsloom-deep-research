import pytest
import pytest_asyncio
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

# Repositories
from backend.api.chat.repository import ChatRepository
from backend.api.session.repository import SessionRepository
from backend.api.auth.repository import UserRepository
from backend.api.account.repository import AccountRepository
from backend.api.assistant.repository import AssistantRepository
from backend.api.kbase.repository import KbaseRepository

# Models
from backend.api.chat.models import MessagePair, Message, MessageList
from backend.api.session.models import UserSession
from backend.api.auth.models import User
from backend.api.assistant.models import Assistant, AssistantConfig, Metadata
from backend.api.kbase.models import KnowledgeBase

# Utils
from backend.util.auth_utils import PasswordService


@pytest_asyncio.fixture(scope="function")
async def chat_dependencies(async_session: AsyncSession):
    """
    1) Ensure we have a root or default account.
    2) Create a user referencing that account.
    3) Create a knowledge base + assistant (for completeness, if your chat includes an assistant).
    4) Create a session referencing the user + assistant (we need session_id).
    Yields (user, session_id, account_id).
    Then cleans up user, assistant, KB, and session after test.
    """

    ### 1) Root/Default Account
    acct_repo = AccountRepository(async_session)
    root_acct = await acct_repo.get_root_account()
    if not root_acct:
        from backend.api.account.models import AccountCreate
        fallback = AccountCreate(
            short_code="rootuser",
            name="Root Account",
            email="root@root.com",
            protection="none"
        )
        root_acct = await acct_repo.create_account(fallback)
        # Mark as root
        await async_session.execute(
            "UPDATE account SET root = TRUE WHERE id = :rid",
            {"rid": str(root_acct.id)},
        )
        await async_session.commit()

    ### 2) User referencing the account
    user_repo = UserRepository(async_session)
    pw_service = PasswordService()
    hashed_pw = pw_service.hash_password("chattestpass")

    test_user = User(
        id=uuid4(),
        account_id=root_acct.account_id,
        account_short_code=root_acct.short_code,
        email="chat_user@example.com",
        password=hashed_pw,
        phone_no="222-333-4444",
        active=True
    )
    created_user = await user_repo.create_user(test_user)

    ### 3) Knowledge Base + Assistant
    kb_repo = KbaseRepository(async_session)
    kb_unique = str(uuid4())[:8]
    kb_data = KnowledgeBase(
        name=f"chat_kbase_{kb_unique}",
        description="KB for chat tests",
        account_short_code=root_acct.short_code
    )
    created_kb = await kb_repo.create_kbase(kb_data)

    asst_repo = AssistantRepository(async_session)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    new_asst = Assistant(
        account_short_code=root_acct.short_code,
        kbase_id=created_kb.id,
        name=f"ChatTestAssistant_{kb_unique}",
        config=config,
        system_prompts={},
        assistant_metadata=Metadata(
            title="ChatTest Assistant",
            description="Assistant for chat tests",
            icon="test_icon.png",
            prompts=[],
            num_history_messages=0
        )
    )
    created_asst = await asst_repo.create_assistant(new_asst)

    ### 4) Create a Session referencing user + assistant
    sess_repo = SessionRepository(async_session)
    session_data = UserSession(
        user_id=created_user.id,
        account_id=created_user.account_id,
        assistant_id=created_asst.id,
        title="ChatTestSession"
    )
    created_session = await sess_repo.set_user_session(session_data)

    # Yield what we need
    yield (created_user, created_session, root_acct)

    # Cleanup in reverse order:
    await sess_repo.delete_user_session(created_session.id)
    await asst_repo.delete_assistant(str(created_asst.id))
    await user_repo.delete_user(created_user.id)
    await kb_repo.delete_kbase(created_kb.id)


@pytest.mark.asyncio
async def test_save_message_pair(async_session: AsyncSession, chat_dependencies):
    """
    Test inserting user + AI messages for a given session, 
    and confirm the repository returns True, then we can retrieve them.
    """
    (user, session_obj, account) = chat_dependencies
    chat_repo = ChatRepository(async_session)

    # 1) Construct a user + AI message
    user_msg = Message(
        role="user",
        content="",
        blocks=[{"type": "text", "content": "Hello, AI!"}],
    )
    ai_msg = Message(
        role="assistant",
        content="",
        blocks=[{"type": "text", "content": "Hello, user!"}],
    )

    pair = MessagePair(
        user_id=user.id,
        account_id=account.account_id,
        user_message=user_msg,
        ai_message=ai_msg,
        session_id=session_obj.id
    )

    # 2) Save the message pair
    saved = await chat_repo.save_message_pair(pair)
    assert saved is True, "Expected save_message_pair(...) to return True"

    # 3) Retrieve messages to confirm
    msgs = await chat_repo.get_messages(session_obj.id)
    assert len(msgs.messages) == 2, "We expect 2 messages (user + AI) in the session"
    # The first is user, second is AI (ordered by created_at ascending)
    user_blocks = msgs.messages[0].blocks
    ai_blocks = msgs.messages[1].blocks
    assert user_blocks == [{"type": "text", "content": "Hello, AI!"}]
    assert ai_blocks == [{"type": "text", "content": "Hello, user!"}]


@pytest.mark.asyncio
async def test_get_messages_with_no_messages(async_session: AsyncSession, chat_dependencies):
    """
    If no messages exist for the session, get_messages should return an empty list.
    """
    (_, session_obj, _) = chat_dependencies
    chat_repo = ChatRepository(async_session)

    empty_list = await chat_repo.get_messages(session_obj.id)
    assert len(empty_list.messages) == 0, "Expected zero messages for this new session"


@pytest.mark.asyncio
async def test_update_message_feedback(async_session: AsyncSession, chat_dependencies):
    """
    Test updating the feedback field for an existing message pair.
    """
    (user, session_obj, account) = chat_dependencies
    chat_repo = ChatRepository(async_session)

    # 1) Insert a message pair
    user_msg = Message(
        role="user",
        content="",
        blocks=[{"type": "text", "content": "Please do X?"}],
    )
    ai_msg = Message(
        role="assistant",
        content="",
        blocks=[{"type": "text", "content": "Here is X."}],
    )
    message_pair = MessagePair(
        user_id=user.id,
        account_id=account.account_id,
        user_message=user_msg,
        ai_message=ai_msg,
        session_id=session_obj.id
    )
    saved_ok = await chat_repo.save_message_pair(message_pair)
    assert saved_ok, "Failed to save the initial message pair."

    # 2) Update feedback to 2 (like a 1-5 rating, etc.)
    feedback_value = 2
    updated_ok = await chat_repo.update_message_feedback(message_pair.message_id, feedback_value)
    assert updated_ok is True, "Expected update_message_feedback(...) to return True"

    # 3) Re-fetch messages and confirm the feedback
    all_msgs = await chat_repo.get_messages(session_obj.id)
    assert len(all_msgs.messages) == 2