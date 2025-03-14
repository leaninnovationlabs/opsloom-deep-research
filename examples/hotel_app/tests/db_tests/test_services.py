import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.db.repositories.service import ServiceRepository
from backend.db.repositories.service_order import ServiceOrderRepository
from backend.schemas.service import ServiceSchema, ServiceOrderSchema
from backend.db.models import Service, ServiceOrders, Reservation, Guest
from datetime import datetime, timedelta

#############
## Test the service repository
##############

@pytest.mark.asyncio
async def test_list_available_services_return_list_service_schema(async_session: AsyncSession):
    """
    tests that list_services in 'ServiceRepository' returns a non-empty list of ServiceSchema objects from our seeded database.
    """
    # Let's seed with services regardless of what's in the database
    # Clean up any existing services first
    await async_session.execute(text("DELETE FROM services"))
    await async_session.commit()
    
    # Add some services - use the valid names from the ValidationError
    services = [
        {
            "name": "room service",
            "price": 199.99,
            "description": "Sumptuous meals and beverages delivered right to your room anytime.",
        },
        {
            "name": "electricity",
            "price": 99.99,
            "description": "Keep the lights on as long as you'd like—our power grid, your wallet!",
        },
        {
            "name": "hot water",
            "price": 212.99,
            "description": "Limited access to hot water. You will be assigned a two-hour window for hot water use.",
        },
    ]
    
    for svc in services:
        async_session.add(Service(
            name=svc["name"],
            description=svc["description"],
            price=svc["price"]
        ))
    
    await async_session.commit()

    # arrange 
    repo = ServiceRepository(db=async_session)

    # act
    services = await repo.list_services()

    # assert
    assert len(services) >= 1, "Expected at least one service to be returned"
    assert isinstance(services[0], ServiceSchema), "Expected item to be an instance of ServiceSchema"

@pytest.mark.asyncio
async def test_get_service_by_id_returns_service_schema(async_session: AsyncSession):
    """
    Tests that 'get_service_by_id' in 'ServiceRepository' returns a single ServiceSchema object from our seeded database.
    """
    # Verify service with ID 1 exists
    result = await async_session.execute(text("SELECT * FROM services WHERE service_id = 1"))
    service_exists = result.first() is not None
    
    if not service_exists:
        # Create service 1 if it doesn't exist - use a valid name from the list in the error
        async_session.add(Service(
            service_id=1,
            name="electricity",  # Using a valid name from the literal list
            description="A service for testing",
            price=9.99
        ))
        await async_session.commit()
    
    # Arrange
    repo = ServiceRepository(db=async_session)

    # Act
    service = await repo.get_service_by_id(service_id=1)

    # Assert
    assert isinstance(service, ServiceSchema), "Expected item to be an instance of ServiceSchema"
    assert service.service_id == 1, "Expected service ID to be 1"

#############
## Test the service orders repository
##############

@pytest.mark.asyncio
async def test_create_service_order_for_electricity_for_guest(async_session: AsyncSession):
    """
    Tests that 'create_service_order' in 'ServiceOrderRepository' creates a new service order for electricity for a guest.
    """
    # First, clean up service orders to avoid duplicates
    await async_session.execute(text("DELETE FROM service_orders"))
    await async_session.commit()
    
    # Create our test guest if needed
    guest_id = "12345678-1234-5678-1234-567812345678"
    guest_result = await async_session.execute(
        text(f"SELECT * FROM guests WHERE guest_id = '{guest_id}'")
    )
    if not guest_result.first():
        async_session.add(Guest(
            guest_id=guest_id,
            full_name="Test Guest",
            email="test.guest@example.com",
            phone="555-555-5555"
        ))
        await async_session.commit()
    
    # Create a test reservation with ID=1 if needed
    res_result = await async_session.execute(
        text("SELECT * FROM reservations WHERE reservation_id = 1")
    )
    if not res_result.first():
        # Delete any existing reservation with ID=1 first
        await async_session.execute(text("DELETE FROM reservations WHERE reservation_id = 1"))
        
        # Create new reservation
        check_in = datetime.now()
        check_out = check_in + timedelta(days=5)
        
        async_session.add(Reservation(
            reservation_id=1,
            guest_id=guest_id,
            room_id=101,
            check_in=check_in,
            check_out=check_out,
            status="confirmed"
        ))
        await async_session.commit()
    
    # Create service ID 3 if needed
    svc_result = await async_session.execute(
        text("SELECT * FROM services WHERE service_id = 3")
    )
    if not svc_result.first():
        async_session.add(Service(
            service_id=3,
            name="electricity",  # Using a valid name
            price=99.99,
            description="Electricity service"
        ))
        await async_session.commit()

    # Arrange
    repo = ServiceOrderRepository(db=async_session)

    service_order = ServiceOrderSchema(
        reservation_id=1,
        service_id=3,  # Electricity
        quantity=1,
        status="pending"
    )

    # Act
    service_order = await repo.create_service_order(service_order=service_order)

    # Assert
    assert service_order.reservation_id == 1, "Expected reservation_id to be 1"
    assert service_order.service_id == 3, "Expected service_id to be 3"
    assert service_order.quantity == 1, "Expected quantity to be 1"
    assert service_order.status == "pending", "Expected status to be 'pending'"

@pytest.mark.asyncio 
async def test_list_service_order_by_reservation_id(async_session: AsyncSession):
    """
    Tests that 'list_service_order_by_reservation_id' in 'ServiceOrderRepository' returns a non-empty list of ServiceOrderSchema objects from our seeded database.
    """
    # We should already have a service order from previous test
    # But let's ensure one exists
    result = await async_session.execute(
        text("SELECT * FROM service_orders WHERE reservation_id = 1")
    )
    if not result.first():
        # Create a service order
        async_session.add(ServiceOrders(
            reservation_id=1,
            service_id=1,
            quantity=1,
            status="pending"
        ))
        await async_session.commit()

    # Arrange
    repo = ServiceOrderRepository(db=async_session)

    # Act
    service_orders = await repo.list_service_order_by_reservation_id(reservation_id=1)

    # Assert
    assert len(service_orders) >= 1, "Expected at least one service order to be returned"
    assert isinstance(service_orders[0], ServiceOrderSchema), "Expected item to be an instance of ServiceOrderSchema"

@pytest.mark.asyncio
async def test_delete_service_order_by_order_id(async_session: AsyncSession):
    """
    Tests that 'delete_service_order' in 'ServiceOrderRepository' deletes a service order from the database.
    """
    # Arrange
    repo = ServiceOrderRepository(db=async_session)

    service_order = ServiceOrderSchema(
        reservation_id=1,
        service_id=1,
        quantity=1,
        status="pending"
    )

    service_order = await repo.create_service_order(service_order=service_order)

    # Act
    await repo.delete_service_order(order_id=service_order.order_id)

    # Assert
    service_order = await repo.get_service_order_by_order_id(order_id=service_order.order_id)

    assert service_order is None, "Expected service order to be None"

@pytest.mark.asyncio
async def test_delete_all_service_orders_for_reservation(async_session: AsyncSession):
    """
    Tests that 'delete_service_orders_by_reservation_id' in 'ServiceOrderRepository' deletes all service orders for a reservation from the database.
    """
    # Arrange
    repo = ServiceOrderRepository(db=async_session)

    service_order = ServiceOrderSchema(
        reservation_id=2,
        service_id=1,
        quantity=1,
        status="pending"
    )

    service_order = await repo.create_service_order(service_order=service_order)

    service_order_2 = ServiceOrderSchema(
        reservation_id=2,
        service_id=2,
        quantity=1,
        status="pending"
    )

    service_order_2 = await repo.create_service_order(service_order=service_order_2)

    # Act
    await repo.delete_service_orders_by_reservation_id(reservation_id=service_order.reservation_id)

    # Assert
    service_orders = await repo.list_service_order_by_reservation_id(reservation_id=service_order.reservation_id)

    assert len(service_orders) == 0, "Expected no service orders to be returned"