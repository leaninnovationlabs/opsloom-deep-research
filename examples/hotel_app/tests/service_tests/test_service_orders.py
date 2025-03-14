# tests/service_tests/test_service_orders.py

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime, timezone

from backend.services.service_orders import ServiceOrderService
from backend.schemas.service import ServiceOrderSchema, ServiceSchema

# Import your DB models for guests, reservations, services, etc.
# Adjust to match your actual code paths
from backend.db.models import Guest, Reservation, Service

@pytest_asyncio.fixture
async def seed_reservations_and_services(async_session: AsyncSession):
    """
    Local fixture: ensures that guests, reservations, and services exist in the DB.
    This prevents ForeignKeyViolationErrors when reservations reference a guest_id 
    that doesn't exist in the 'guests' table.
    """

    # 1) Delete all relevant tables (SQLite doesn't support TRUNCATE)
    # Include `guests` because reservations reference guests
    await async_session.execute(text("DELETE FROM service_orders"))
    await async_session.execute(text("DELETE FROM reservations"))
    await async_session.execute(text("DELETE FROM services"))
    await async_session.execute(text("DELETE FROM guests"))
    await async_session.commit()

    # 2) Insert the needed Guest rows
    guest1 = Guest(
        guest_id="00000000-0000-0000-0000-000000000001",
        full_name="Guest #1",
        email="guest1@example.com",
    )
    guest2 = Guest(
        guest_id="00000000-0000-0000-0000-000000000002",
        full_name="Guest #2",
        email="guest2@example.com",
    )
    guest3 = Guest(
        guest_id="00000000-0000-0000-0000-000000000003",
        full_name="Guest #3",
        email="guest3@example.com",
    )
    async_session.add_all([guest1, guest2, guest3])
    await async_session.flush()

    # 3) Insert reservations #1,2,3, referencing the above guest IDs
    check_in_1 = datetime(2025, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    check_out_1 = datetime(2025, 1, 3, 10, 0, 0, tzinfo=timezone.utc)

    check_in_2 = datetime(2025, 2, 1, 12, 0, 0, tzinfo=timezone.utc)
    check_out_2 = datetime(2025, 2, 5, 10, 0, 0, tzinfo=timezone.utc)

    check_in_3 = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    check_out_3 = datetime(2025, 3, 4, 10, 0, 0, tzinfo=timezone.utc)

    res1 = Reservation(
        reservation_id=1,
        guest_id="00000000-0000-0000-0000-000000000001",  # must match existing guest
        room_id=101,
        check_in=check_in_1,
        check_out=check_out_1,
        status="confirmed",
    )
    res2 = Reservation(
        reservation_id=2,
        guest_id="00000000-0000-0000-0000-000000000002",
        room_id=102,
        check_in=check_in_2,
        check_out=check_out_2,
        status="confirmed",
    )
    res3 = Reservation(
        reservation_id=3,
        guest_id="00000000-0000-0000-0000-000000000003",
        room_id=103,
        check_in=check_in_3,
        check_out=check_out_3,
        status="confirmed",
    )

    # 4) Insert services #1,2
    svc1 = Service(
        service_id=1,
        name="room service",
        description="Basic room service",
        price=9.99
    )
    svc2 = Service(
        service_id=2,
        name="wake up call",
        description="Morning call service",
        price=3.99
    )

    # 5) Add and commit
    async_session.add_all([res1, res2, res3, svc1, svc2])
    await async_session.commit()

    # Let the tests run
    yield


@pytest.mark.asyncio
async def test_list_all_services(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    services = await service.list_all_services()
    assert isinstance(services, list)
    assert len(services) >= 1, "Expected at least one service"
    assert all(isinstance(s, ServiceSchema) for s in services)

@pytest.mark.asyncio
async def test_get_service_by_id(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    service_obj = await service.get_service_by_id(service_id=1)
    assert isinstance(service_obj, ServiceSchema)
    assert service_obj.service_id == 1

    with pytest.raises(ValueError):
        await service.get_service_by_id(999999)

@pytest.mark.asyncio
async def test_create_service_order(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    created_order = await service.create_service_order(
        reservation_id=1,
        service_id=1,
        quantity=2,
        status="pending"
    )
    assert isinstance(created_order, ServiceOrderSchema)
    assert created_order.reservation_id == 1
    assert created_order.service_id == 1

@pytest.mark.asyncio
async def test_list_service_orders_by_reservation_id(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    new_order = await service.create_service_order(
        reservation_id=1,
        service_id=1,
        quantity=2,
        status="pending"
    )
    orders = await service.list_service_orders_by_reservation_id(reservation_id=1)
    assert len(orders) > 0
    assert any(o.order_id == new_order.order_id for o in orders)

@pytest.mark.asyncio
async def test_delete_service_order(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    created_order = await service.create_service_order(
        reservation_id=2,
        service_id=2,
        quantity=1,
        status="pending"
    )
    deleted = await service.delete_service_order(order_id=created_order.order_id)
    assert deleted is True

    orders = await service.list_service_orders_by_reservation_id(reservation_id=2)
    assert all(o.order_id != created_order.order_id for o in orders)

@pytest.mark.asyncio
async def test_delete_service_orders_for_reservation(async_session, seed_reservations_and_services):
    service = ServiceOrderService(db=async_session)
    await service.create_service_order(
        reservation_id=3,
        service_id=1,
        quantity=1,
        status="pending"
    )
    await service.create_service_order(
        reservation_id=3,
        service_id=2,
        quantity=2,
        status="pending"
    )
    await service.delete_service_orders_for_reservation(reservation_id=3)
    remaining = await service.list_service_orders_by_reservation_id(reservation_id=3)
    assert len(remaining) == 0, "Expected no service orders left for reservation_id=3"