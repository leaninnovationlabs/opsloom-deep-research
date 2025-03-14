import pytest
import uuid
from uuid import UUID
from backend.api.assistant.services import AssistantService
from backend.api.assistant.repository import AssistantRepository
from backend.api.assistant.models import Assistant, AssistantConfig, Metadata
from backend.api.kbase.repository import KbaseRepository
from backend.api.kbase.models import KnowledgeBase
from sqlalchemy.ext.asyncio import AsyncSession
import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def kbase_setup(async_session: AsyncSession):
    """Fixture to create a temporary knowledge base for assistant tests"""
    kb_repo = KbaseRepository(async_session)
    unique_suffix = str(uuid.uuid4())[:8]
    kb_data = KnowledgeBase(
        name=f"assistant_test_kbase_{unique_suffix}",
        description="Temporary Kbase for Assistant Tests",
        account_short_code="default"
    )
    created_kbase = await kb_repo.create_kbase(kb_data)
    yield created_kbase
    await kb_repo.delete_kbase(created_kbase.id)

@pytest.mark.asyncio
async def test_create_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test creating an assistant through service layer"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    unique_suffix = str(uuid.uuid4())[:8]
    config = AssistantConfig(
        provider="openai",
        type="rag",
        model="gpt-4o",
        table_name="my_table"
    )
    meta = Metadata(
        title="Test Title",
        description="Test Description",
        prompts=[
            "Prompt 1"
        ],
        icon="test.png"
    )
    
    # Act
    created = await service.create_assistant(Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name=f"TestAssistant_{unique_suffix}",
        config=config,
        system_prompts={"greeting": "Hello"},
        metadata=meta
    ))
    
    # Assert
    assert created.id is not None
    assert created.name == f"TestAssistant_{unique_suffix}"
    assert created.config.provider == "openai"
    assert created.assistant_metadata.title == "Test Title"
    
    # Cleanup
    await repo.delete_assistant(str(created.id))

@pytest.mark.asyncio
async def test_get_assistant_by_id(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test retrieving assistant by ID through service"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    assistant_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="FindMeAssistant",
        config=config,
        system_prompts={}
    )
    created = await service.create_assistant(assistant_in)
    
    # Act
    fetched = await service.get_assistant(created.id)
    
    # Assert
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "FindMeAssistant"
    
    # Cleanup
    await repo.delete_assistant(str(created.id))

@pytest.mark.asyncio
async def test_update_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test updating assistant properties through service"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    assistant_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="OriginalName",
        config=config,
        system_prompts={}
    )
    created = await service.create_assistant(assistant_in)
    
    # Act
    created.name = "UpdatedName"
    created.config.model = "gpt-4"
    updated = await service.update_assistant(created)
    
    # Assert
    assert updated.name == "UpdatedName"
    assert updated.config.model == "gpt-4"
    
    # Cleanup
    await repo.delete_assistant(str(created.id))

@pytest.mark.asyncio
async def test_list_assistants(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test listing assistants through service"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    unique_suffix = str(uuid.uuid4())[:8]
    
    # Create two assistants
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a1 = await service.create_assistant(Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name=f"First_{unique_suffix}",
        config=config,
        system_prompts={}
    ))
    a2 = await service.create_assistant(Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name=f"Second_{unique_suffix}",
        config=config,
        system_prompts={}
    ))
    
    # Act
    assistants = await service.list_assistants("default")
    
    # Assert
    assert len(assistants.assistants) >= 2
    assert any(a.id == a1.id for a in assistants.assistants)
    assert any(a.id == a2.id for a in assistants.assistants)
    
    # Cleanup
    await repo.delete_assistant(str(a1.id))
    await repo.delete_assistant(str(a2.id))

@pytest.mark.asyncio
async def test_deactivate_and_reactivate_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test lifecycle state changes through service"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    assistant_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="StateChangeTest",
        config=config,
        system_prompts={}
    )
    created = await service.create_assistant(assistant_in)
    
    # Act & Assert: Deactivate
    assert await service.deactivate_assistant(created.id) is True
    listed = await service.list_assistants("default")
    assert not any(a.id == created.id for a in listed.assistants)
    
    # Act & Assert: Reactivate
    assert await service.reactivate_assistant(created.id) is True
    listed = await service.list_assistants("default")
    assert any(a.id == created.id for a in listed.assistants)
    
    # Cleanup
    await repo.delete_assistant(str(created.id))

@pytest.mark.asyncio
async def test_delete_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """Test permanent deletion through service"""
    # Arrange
    repo = AssistantRepository(async_session)
    service = AssistantService(repo)
    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    assistant_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="DeleteTest",
        config=config,
        system_prompts={}
    )
    created = await service.create_assistant(assistant_in)
    
    # Act
    result = await service.delete_assistant(created.id)
    
    # Assert
    assert result is True
    assert await service.get_assistant(created.id) is None