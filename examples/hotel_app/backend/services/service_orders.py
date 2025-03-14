import logging
from typing import List

from backend.db.repositories.service import ServiceRepository
from backend.db.repositories.reservation import ReservationRepository
from backend.schemas.reservation import ReservationSchema
from backend.db.repositories.service_order import ServiceOrderRepository
from backend.schemas.service import ServiceSchema, ServiceOrderSchema

logger = logging.getLogger(__name__)

class ServiceOrderService:
    """
    A service layer class for managing service orders, 
    orchestrating Service and ServiceOrder repositories.

    Exposed methods (AI-agent friendly):
    - list_all_services(...)
    - get_service_by_id(...)
    - create_service_order(...)
    - list_service_orders_by_reservation_id(...)
    - update_service_order(...)
    - delete_service_order(...)
    - delete_service_orders_for_reservation(...)
    """

    def __init__(self, db):
        self.db = db
        self.service_repo = ServiceRepository(db=db)
        self.service_order_repo = ServiceOrderRepository(db=db)
        self.reservation_repo = ReservationRepository(db=db)

    async def list_all_services(self) -> List[ServiceSchema]:
        """
        Return a list of all available services from the database.
        """
        services = await self.service_repo.list_services()
        return services

    async def get_service_by_id(self, service_id: int) -> ServiceSchema:
        """
        Return a single service by its ID.
        Raises ValueError if no such service exists.
        """
        service = await self.service_repo.get_service_by_id(service_id=service_id)
        if not service:
            raise ValueError(f"Service with id={service_id} not found.")
        return service

    async def create_service_order(
        self,
        reservation_id: int,
        service_id: int,
        quantity: int,
        status: str = "pending"
    ) -> ServiceOrderSchema:
        """
        Create a new service order for a given reservation and service, 
        returning the newly created ServiceOrderSchema.
        """
        # validate that reservation exists
        reservation = await self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Cannot create order. Reservation with id={reservation_id} not found.")

        # Optional: Validate that service_id actually exists
        service = await self.service_repo.get_service_by_id(service_id)
        if not service:
            raise ValueError(f"Cannot create order. Service with id={service_id} not found.")

        new_order = ServiceOrderSchema(
            reservation_id=reservation_id,
            service_id=service_id,
            quantity=quantity,
            status=status
        )
        created = await self.service_order_repo.create_service_order(new_order)
        return created

    async def list_service_orders_by_reservation_id(self, reservation_id: int) -> List[ServiceOrderSchema]:
        """
        Return all service orders associated with a particular reservation_id.
        """
        # check if reservation exists
        reservation = await self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation with id={reservation_id} not found.")

        orders = await self.service_order_repo.list_service_order_by_reservation_id(reservation_id)
        return orders

    async def delete_service_order(self, order_id: int) -> bool:
        """
        Delete a single service order by its order_id. 
        Returns True if successfully deleted; otherwise raises ValueError.
        """
        order = await self.service_order_repo.get_service_order_by_order_id(order_id)
        if not order:
            raise ValueError(f"Service order with id={order_id} not found.")

        await self.service_order_repo.delete_service_order(order_id)
        return True

    async def delete_service_orders_for_reservation(self, reservation_id: int) -> bool:
        """
        Delete all service orders for a given reservation_id. Returns True if successful.
        """
        # check if reservation exists
        reservation = await self.reservation_repo.get_reservation_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"Reservation with id={reservation_id} not found.")
        
        # check if any orders exist for this reservation
        orders = await self.service_order_repo.list_service_order_by_reservation_id(reservation_id)
        if not orders:
            raise ValueError(f"Reservation with id={reservation_id} has no orders to delete.")

        await self.service_order_repo.delete_service_orders_by_reservation_id(reservation_id)
        return True
