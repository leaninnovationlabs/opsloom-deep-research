import pytest
import pytest_asyncio
from uuid import UUID, uuid4
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

# Service and Models
from backend.api.chat.services import ChatService
from backend.api.chat.models import ChatRequest, Message, MessagePair, FeedbackRequest
from backend.api.session.models import UserSession
from backend.util.auth_utils import TokenData

# Fixture dependencies
from tests.db_tests.test_chat import chat_dependencies  # Reuse existing fixture

@pytest.fixture
def mock_ai_response_service(mocker):
    """Mock AIResponseService to return predictable responses"""
    mock = mocker.patch('backend.api.chat.services.AIResponseService')
    mock_instance = mock.return_value
    mock_instance.initialize = AsyncMock()
    
    # Correctly mock the async generator
    async def mock_stream(*args, **kwargs):
        yield {'content': 'Test', 'type': 'text'}
        yield {'content': ' response', 'type': 'text'}
    
    # Use MagicMock and set return_value to the async generator
    mock_instance.get_ai_response_stream = MagicMock(return_value=mock_stream())
    mock_instance.get_summary_title = AsyncMock(return_value="Generated Title")
    return mock

@pytest.mark.asyncio
async def test_process_chat_request(
    async_session: AsyncSession, 
    chat_dependencies,
    mock_ai_response_service
):
    """Test complete chat request processing flow"""
    # Arrange
    user, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    current_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,
        email=user.email,
        scopes=[]
    )
    
    request = ChatRequest(
        session_id=str(session.id),
        message=Message(
            role="user",
            content="Test question",
            blocks=[{"type": "text", "text": "Test question"}]
        )
    )

    # Create BackgroundTasks instance
    background_tasks = BackgroundTasks()

    # Act
    response_stream = await service.process_chat_request(
        request, 
        current_user,
        background_tasks  # Pass the instance
    )
    
    # Collect responses
    responses = []
    async for chunk in response_stream:
        responses.append(chunk)

    # Execute background tasks
    await background_tasks()  # Trigger task execution

    # Assert
    assert len(responses) >= 2
    
    # Verify messages were stored
    messages = await service.get_messages(str(session.id), current_user)
    assert len(messages.messages) == 2

@pytest.mark.asyncio
async def test_validate_session_valid(async_session: AsyncSession, chat_dependencies):
    """Test successful session validation"""
    # Arrange
    user, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    current_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,
        email=user.email,
        scopes=[]
    )

    # Act
    validated_session = await service.validate_session(str(session.id), current_user)

    # Assert
    assert validated_session.id == session.id

@pytest.mark.asyncio
async def test_validate_session_invalid_user(async_session: AsyncSession, chat_dependencies):
    """Test session validation with invalid user"""
    # Arrange
    _, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    invalid_user = TokenData(
        user_id=str(uuid4()),  # Random user ID
        account_id=str(uuid4()),
        account_short_code="invalid",
        email="invalid@test.com",
        scopes=[]
    )

    # Act/Assert
    with pytest.raises(HTTPException) as exc_info:
        await service.validate_session(str(session.id), invalid_user)
    
    assert exc_info.value.status_code == 403

@pytest.mark.asyncio
async def test_store_message_pair(async_session: AsyncSession, chat_dependencies):
    """Test storing message pairs in the database"""
    # Arrange
    user, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    pair = MessagePair(
        user_message=Message(
            role="user",
            content="Test",
            blocks=[{"type": "text", "text": "Test"}]
        ),
        ai_message=Message(
            role="ai",
            content="Response",
            blocks=[{"type": "text", "text": "Response"}]
        ),
        user_id=user.id,
        account_id=user.account_id,
        session_id=session.id
    )

    # Act
    result = await service.store_message_pair(session, ChatRequest(
        session_id=str(session.id),
        message=pair.user_message
    ), pair.ai_message)

    # Assert
    messages = await service.get_messages(str(session.id), TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,
        email=user.email,
        scopes=[]
    ))
    assert len(messages.messages) == 2

@pytest.mark.asyncio
async def test_get_messages_empty(async_session: AsyncSession, chat_dependencies):
    """Test retrieving messages from an empty session"""
    # Arrange
    user, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    current_user = TokenData(
        user_id=str(user.id),
        account_id=str(user.account_id),
        account_short_code=user.account_short_code,
        email=user.email,
        scopes=[]
    )

    # Act
    messages = await service.get_messages(str(session.id), current_user)

    # Assert
    assert len(messages.messages) == 0

@pytest.mark.asyncio
async def test_submit_feedback(async_session: AsyncSession, chat_dependencies):
    """Test submitting feedback for a message"""
    # Arrange
    user, session, _ = chat_dependencies
    service = ChatService(async_session)
    
    # Create test message
    pair = MessagePair(
        user_message=Message(role="user", content="Test", blocks=[]),
        ai_message=Message(role="ai", content="Response", blocks=[]),
        user_id=user.id,
        account_id=user.account_id,
        session_id=session.id
    )
    await service.chat_repository.save_message_pair(pair)

    # Create FeedbackRequest instead of dict
    feedback_request = FeedbackRequest(
        message_id=str(pair.message_id),
        feedback=5
    )

    # Act
    result = await service.submit_feedback(
        feedback_request,
        TokenData(
            user_id=str(user.id),
            account_id=str(user.account_id),
            account_short_code=user.account_short_code,
            email=user.email,
            scopes=[]
        )
    )

    # Assert
    assert result is True