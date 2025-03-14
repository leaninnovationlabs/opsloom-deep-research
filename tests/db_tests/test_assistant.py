import pytest
import pytest_asyncio
import uuid

from backend.api.kbase.repository import KbaseRepository
from backend.api.kbase.models import KnowledgeBase
from backend.api.assistant.models import (
    Assistant,
    AssistantConfig,
    Metadata
)
from backend.api.assistant.repository import AssistantRepository
from sqlalchemy.ext.asyncio import AsyncSession


@pytest_asyncio.fixture(scope="function")
async def kbase_setup(async_session: AsyncSession):
    kb_repo = KbaseRepository(async_session)

    # Use a unique name: “assistant_test_kbase_<random UUID>”
    unique_suffix = str(uuid.uuid4())[:8]
    kb_data = KnowledgeBase(
        name=f"assistant_test_kbase_{unique_suffix}",
        description="Temporary Kbase for Assistant Tests",
        account_short_code="default"
    )
    created_kbase = await kb_repo.create_kbase(kb_data)
    yield created_kbase
    await kb_repo.delete_kbase(created_kbase.id)



# @pytest_asyncio.fixture(scope="function")
# async def cleanup_assistant(async_session: AsyncSession):
#     """
#     Ensure the 'assistant' table is cleaned up before/after each test.
#     By default, this fixture will run for each test in this module.
#     """
#     # If you want to clean up before each test, do it here
#     yield
#     # Clean up after each test
#     await async_session.execute("TRUNCATE TABLE assistant CASCADE;")
#     await async_session.commit()


@pytest.mark.asyncio
async def test_create_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Test creating an Assistant row and verifying we get a valid record back.
    """
    repo = AssistantRepository(async_session)

    # Example config that should pass validation
    config = AssistantConfig(
        provider="openai",
        type="rag",
        model="gpt-4o",
        table_name="my_assistant_table"
    )

    meta = Metadata(
        title="Test Title",
        description="Just a test assistant",
        icon="test_icon.png",
        prompts=["Hello", "World"],
        num_history_messages=2
    )

    unique_suffix = str(uuid.uuid4())[:8]

    # Build an Assistant with our Kbase ID
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name=f"MyFirstAssistant{unique_suffix}",
        config=config,
        system_prompts={"initial": "Hello user!"},
        metadata=meta
    )

    # Create and verify
    created = await repo.create_assistant(a_in)
    assert created is not None, "Assistant creation returned None"
    assert created.id is not None, "Assistant ID should not be None"
    assert created.name == f"MyFirstAssistant{unique_suffix}"
    assert created.config.provider == "openai"
    assert created.assistant_metadata.title == "Test Title"

    await repo.delete_assistant(str(created.id))


@pytest.mark.asyncio
async def test_get_assistant_by_id(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Create an assistant, then fetch it by ID.
    """
    repo = AssistantRepository(async_session)

    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="AssistantToFind",
        config=config,
        system_prompts={},
        metadata=None
    )
    created = await repo.create_assistant(a_in)
    assert created is not None

    fetched = await repo.get_assistant_by_id(str(created.id))
    assert fetched is not None, "Fetching by ID returned None"
    assert fetched.id == created.id
    assert fetched.name == "AssistantToFind"

    await repo.delete_assistant(str(created.id))


@pytest.mark.asyncio
async def test_update_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Create an assistant, then update its name and config, verifying the changes are persisted.
    """
    repo = AssistantRepository(async_session)

    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="AssistantBeforeUpdate",
        config=config,
        system_prompts={"initial": "Hello"},
        metadata=None
    )
    created = await repo.create_assistant(a_in)
    assert created is not None

    # Modify it
    created.name = "AssistantAfterUpdate"
    created.config.model = "gpt-4"

    updated = await repo.update_assistant(created)
    assert updated is not None, "Update returned None"
    assert updated.name == "AssistantAfterUpdate"
    assert updated.config.model == "gpt-4"

    await repo.delete_assistant(str(created.id))


@pytest.mark.asyncio
async def test_list_assistants(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Create multiple assistants, then list all of them by account_short_code.
    """
    repo = AssistantRepository(async_session)

    # Create two assistants
    config1 = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a1 = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="AssistantOne",
        config=config1,
        system_prompts={},
        metadata=None
    )
    await repo.create_assistant(a1)

    config2 = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a2 = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="AssistantTwo",
        config=config2,
        system_prompts={},
        metadata=None
    )
    await repo.create_assistant(a2)

    # List them
    assistants_list = await repo.list_assistants("default")
    assert len(assistants_list.assistants) >= 2
    names = [a.name for a in assistants_list.assistants]
    assert "AssistantOne" in names
    assert "AssistantTwo" in names

    # Clean up
    await repo.delete_assistant(str(a1.id))
    await repo.delete_assistant(str(a2.id))


@pytest.mark.asyncio
async def test_deactivate_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Test that we can mark an assistant as inactive.
    """
    repo = AssistantRepository(async_session)

    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="DeactivateMe",
        config=config,
        system_prompts={},
        metadata=None
    )
    created = await repo.create_assistant(a_in)
    assert created is not None

    success = await repo.deactivate_assistant(str(created.id))
    assert success is True

    # Confirm that if we list active assistants, we no longer see it
    listed = await repo.list_assistants("default")
    assert not any(a.id == created.id for a in listed.assistants), "Deactivated assistant still found in list"

    await repo.delete_assistant(str(created.id))


@pytest.mark.asyncio
async def test_reactivate_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Test that we can mark an assistant as active again.
    """
    repo = AssistantRepository(async_session)

    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="ReactivateMe",
        config=config,
        system_prompts={},
        metadata=None
    )
    created = await repo.create_assistant(a_in)
    assert created is not None

    # Deactivate first
    _ = await repo.deactivate_assistant(str(created.id))

    # Reactivate
    success = await repo.reactivate_assistant(str(created.id))
    assert success is True

    # Confirm we see it in the list again
    listed = await repo.list_assistants("default")
    assert any(a.id == created.id for a in listed.assistants), "Reactivated assistant not found in list"

    await repo.delete_assistant(str(created.id))


@pytest.mark.asyncio
async def test_delete_assistant(async_session: AsyncSession, kbase_setup: KnowledgeBase):
    """
    Test permanently deleting an assistant from the DB.
    """
    repo = AssistantRepository(async_session)

    config = AssistantConfig(provider="openai", type="rag", model="gpt-4o")
    a_in = Assistant(
        account_short_code="default",
        kbase_id=kbase_setup.id,
        name="DeleteMeAssistant",
        config=config,
        system_prompts={},
        metadata=None
    )
    created = await repo.create_assistant(a_in)
    assert created is not None

    success = await repo.delete_assistant(str(created.id))
    assert success is True

    # Verify it is indeed gone
    fetched = await repo.get_assistant_by_id(str(created.id))
    assert fetched is None, "Deleted assistant still returned by get_assistant_by_id"
