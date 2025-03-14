import pytest
from uuid import UUID
from backend.api.kbase.services import KbaseService
from backend.api.kbase.repository import KbaseRepository
from backend.api.kbase.models import KnowledgeBase

@pytest.mark.asyncio
async def test_create_kbase(async_session):
    """Test creating a knowledge base via the service."""
    # Arrange
    repo = KbaseRepository(async_session)
    service = KbaseService(repo)
    kb_data = KnowledgeBase(
        name="test_service_create",
        description="Service test",
        account_short_code="default"
    )
    
    # Act
    created_kb = await service.create_kbase(kb_data)
    
    # Assert
    assert created_kb is not None
    assert created_kb.id is not None
    assert created_kb.name == kb_data.name
    assert created_kb.description == kb_data.description
    assert created_kb.account_short_code == kb_data.account_short_code
    
    # Cleanup
    await repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_list_kbases(async_session):
    """Test listing all knowledge bases via the service."""
    # Arrange
    repo = KbaseRepository(async_session)
    service = KbaseService(repo)
    kb_data = KnowledgeBase(
        name="test_service_list",
        description="List test",
        account_short_code="default"
    )
    created_kb = await service.create_kbase(kb_data)
    
    # Act
    kb_list = await service.list_kbases()
    
    # Assert
    assert any(kb.id == created_kb.id for kb in kb_list.kbases)
    
    # Cleanup
    await repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_get_kbase(async_session):
    """Test retrieving a knowledge base by ID via the service."""
    # Arrange
    repo = KbaseRepository(async_session)
    service = KbaseService(repo)
    kb_data = KnowledgeBase(
        name="test_service_get",
        description="Get test",
        account_short_code="default"
    )
    created_kb = await service.create_kbase(kb_data)
    
    # Act
    fetched_kb = await service.get_kbase(created_kb.id)
    
    # Assert
    assert fetched_kb is not None
    assert fetched_kb.id == created_kb.id
    assert fetched_kb.name == kb_data.name
    assert fetched_kb.description == kb_data.description
    
    # Cleanup
    await repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_update_kbase(async_session):
    """Test updating a knowledge base via the service."""
    # Arrange
    repo = KbaseRepository(async_session)
    service = KbaseService(repo)
    kb_data = KnowledgeBase(
        name="test_service_update",
        description="Update test",
        account_short_code="default"
    )
    created_kb = await service.create_kbase(kb_data)
    created_kb.name = "updated_name"
    created_kb.description = "updated description"
    
    # Act
    updated_kb = await service.update_kbase(created_kb)
    
    # Assert
    assert updated_kb is not None
    assert updated_kb.id == created_kb.id
    assert updated_kb.name == "updated_name"
    assert updated_kb.description == "updated description"
    
    # Cleanup
    await repo.delete_kbase(created_kb.id)

@pytest.mark.asyncio
async def test_delete_kbase(async_session):
    """Test deleting a knowledge base via the service."""
    # Arrange
    repo = KbaseRepository(async_session)
    service = KbaseService(repo)
    kb_data = KnowledgeBase(
        name="test_service_delete",
        description="Delete test",
        account_short_code="default"
    )
    created_kb = await service.create_kbase(kb_data)
    
    # Act
    delete_result = await service.delete_kbase(created_kb.id)
    
    # Assert
    assert delete_result is True
    deleted_kb = await repo.get_kbase_by_id(created_kb.id)
    assert deleted_kb is None