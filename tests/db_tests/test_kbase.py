import pytest
from backend.api.kbase.repository import KbaseRepository
from backend.api.kbase.models import KnowledgeBase

@pytest.mark.asyncio
async def test_create_kbase(async_session):
    """
    Test creating a knowledge base via the repository.
    """
    repo = KbaseRepository(async_session)
    kb_data = KnowledgeBase(
        name="test1",
        description="A test knowledge base.",
        account_short_code="default"
    )
    created_kb = await repo.create_kbase(kb_data)

    assert created_kb is not None
    assert created_kb.id is not None
    assert created_kb.name == "test1"
    assert created_kb.account_short_code == "default"

    await repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_get_kbase_by_id(async_session):
    repo = KbaseRepository(async_session)
    # First create a KBase
    kb_data = KnowledgeBase(
        name="test2",
        description="Find me by ID",
        account_short_code="default"
    )
    created_kb = await repo.create_kbase(kb_data)
    kb_id = created_kb.id

    # Retrieve by ID
    fetched_kb = await repo.get_kbase_by_id(kb_id)
    assert fetched_kb is not None
    assert fetched_kb.id == kb_id
    assert fetched_kb.name == "test2"

    await repo.delete_kbase(kb_id)
    
@pytest.mark.asyncio
async def test_get_kbase_by_name(async_session):
    repo = KbaseRepository(async_session)
    kb_data = KnowledgeBase(
        name="test3",
        description="Find me by name",
        account_short_code="default"
    )
    await repo.create_kbase(kb_data)

    found = await repo.get_kbase_by_name("test3")
    assert found is not None
    assert found.name == "test3"

    await repo.delete_kbase(found.id)

@pytest.mark.asyncio
async def test_list_kbases(async_session):
    repo = KbaseRepository(async_session)

    kb_data = KnowledgeBase(
        name="test3",
        description="Find me by name",
        account_short_code="default"
    )
    await repo.create_kbase(kb_data)


    kb_list = await repo.list_kbases()
    assert len(kb_list.kbases) >= 1  # We expect at least 3 in total

    await repo.delete_kbase(kb_data.id)

@pytest.mark.asyncio
async def test_update_kbase(async_session):
    repo = KbaseRepository(async_session)
    # Create
    kb_data = KnowledgeBase(name="UpdateMe", description="old desc", account_short_code="default")
    created_kb = await repo.create_kbase(kb_data)

    # Update
    created_kb.name = "test5"
    created_kb.description = "new desc2"
    updated_kb = await repo.update_kbase(created_kb)

    assert updated_kb is not None
    assert updated_kb.name == "test5"
    assert updated_kb.description == "new desc2"

    await repo.delete_kbase(updated_kb.id)

@pytest.mark.asyncio
async def test_delete_kbase(async_session):
    repo = KbaseRepository(async_session)
    # Create a KB
    kb_data = KnowledgeBase(name="DeleteMe")
    created_kb = await repo.create_kbase(kb_data)
    kb_id = created_kb.id

    # Delete
    success = await repo.delete_kbase(kb_id)
    assert success is True

    # Confirm it's gone
    fetched = await repo.get_kbase_by_id(kb_id)
    assert fetched is None