from sqlalchemy import select, update, delete
from backend.schemas.reservation import ReservationSchema
from backend.db.models import Reservation  # your ORM model
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ReservationRepository:
    def __init__(self, db):
        self.db = db

    async def create_reservation(self, reservation: ReservationSchema) -> ReservationSchema:
        """
        Create a new reservation in the database.
        """
        # Validate check-in and check-out dates
        if reservation.check_in >= reservation.check_out:
            raise ValueError("check_in must be before check_out")
            
        # Always convert guest_id to string for SQLite compatibility
        guest_id = str(reservation.guest_id) if hasattr(reservation.guest_id, '__str__') else reservation.guest_id
            
        db_obj = Reservation(
            guest_id=guest_id,
            room_id=reservation.room_id,
            check_in=reservation.check_in,
            check_out=reservation.check_out,
            status=reservation.status
        )
        self.db.add(db_obj)
        await self.db.flush()
        # refresh to get updated_at, created_at, etc.
        await self.db.refresh(db_obj)

        await self.db.commit()
        return ReservationSchema.model_validate(db_obj)

    async def list_reservations(self) -> List[ReservationSchema]:
        """
        Fetch all reservations from the database.
        """
        result = await self.db.execute(select(Reservation))
        rows = result.scalars().all()
        return [ReservationSchema.model_validate(r) for r in rows]

    async def get_reservation_by_id(self, reservation_id: int) -> Optional[Reservation]:
        """
        Fetch a reservation by ID.
        """
        result = await self.db.execute(
            select(Reservation).where(Reservation.reservation_id == reservation_id)
        )
        return result.scalar_one_or_none()

    async def list_reservations_by_guest_id(self, guest_id) -> List[ReservationSchema]:
        """
        Fetch all reservations for a specific guest.
        """
        # Always convert to string for SQLite compatibility
        guest_id_str = str(guest_id) if hasattr(guest_id, '__str__') else guest_id
            
        result = await self.db.execute(
            select(Reservation).where(Reservation.guest_id == guest_id_str)
        )
        rows = result.scalars().all()
        return [ReservationSchema.model_validate(r) for r in rows]

    async def update_reservation(
        self, 
        reservation_id: int, 
        new_check_in: datetime, 
        new_check_out: datetime, 
        new_room_id: int
    ) -> ReservationSchema:
        """
        Update an existing reservation.
        """
        # Validate check-in and check-out dates
        if new_check_in >= new_check_out:
            raise ValueError("check_in must be before check_out")
            
        # fetch the existing object
        db_obj = await self.get_reservation_by_id(reservation_id)
        if not db_obj:
            return None
        
        db_obj.check_in = new_check_in
        db_obj.check_out = new_check_out
        db_obj.room_id = new_room_id
        
        # status might remain, or you can handle changes
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)

        await self.db.commit()
        return ReservationSchema.model_validate(db_obj)

    async def delete_reservation(self, reservation_id: int) -> bool:
        """
        Delete a reservation by ID.
        """
        db_obj = await self.get_reservation_by_id(reservation_id)
        if not db_obj:
            return False
        
        await self.db.delete(db_obj)
        await self.db.flush()

        await self.db.commit()
        return True