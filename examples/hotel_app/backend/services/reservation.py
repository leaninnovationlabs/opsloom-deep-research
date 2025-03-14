import logging
from datetime import datetime
from typing import List, Optional
import random
from uuid import UUID

from backend.db.repositories.guest import GuestRepository
from backend.db.repositories.room import RoomRepository
from backend.db.repositories.reservation import ReservationRepository
from backend.schemas.guest import GuestSchema
from backend.schemas.reservation import ReservationSchema
from datetime import timezone

logger = logging.getLogger(__name__)

def ensure_utc(dt: datetime) -> datetime:
    """Convert naive or offset-aware datetime to offset-aware UTC."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    else:
        return dt.astimezone(timezone.utc)

class ReservationService:
    def __init__(self, db):
        self.db = db
        self.guest_repo = GuestRepository(db=db)
        self.room_repo = RoomRepository(db=db)
        self.reservation_repo = ReservationRepository(db=db)

    async def create_reservation(
        self,
        guest: GuestSchema,
        room_type: str,
        check_in: datetime,
        check_out: datetime
    ) -> ReservationSchema:
        """
        Creates a new reservation for a given guest, room type, and date range.
        """
        # 1) Confirm guest exists or create if needed
        try:
            # Handle guest_id as string
            guest_id = guest.guest_id
            if isinstance(guest_id, UUID):
                guest_id = str(guest_id)
                
            existing_guest = await self.guest_repo.get_guest_by_id(guest_id)
        except ValueError:
            guest = await self.guest_repo.create_guest(guest)
            
        # Convert all times to UTC offset-aware
        check_in = ensure_utc(check_in)
        check_out = ensure_utc(check_out)

        if check_out <= check_in:
            raise ValueError("Check-out date must be after check-in date.")

        # 2) Decide the room range
        room_type = room_type.lower()
        if room_type == "single":
            possible_rooms = range(101, 111)
        elif room_type == "double":
            possible_rooms = range(111, 121)
        elif room_type == "suite":
            possible_rooms = range(121, 131)
        else:
            raise ValueError(f"Invalid room type '{room_type}'")

        # 3) Pick a random room from the possible range
        selected_room_id = random.choice(list(possible_rooms))

        # Ensure we have a string guest_id for SQLite compatibility
        guest_id = guest.guest_id
        if isinstance(guest_id, UUID):
            guest_id = str(guest_id)

        # 4) Check for overlap with existing reservations for this guest on the same room
        existing_res_for_guest = await self.reservation_repo.list_reservations_by_guest_id(guest_id)
        for res in existing_res_for_guest:
            if res.room_id == selected_room_id:
                # everything in UTC for comparison
                guest_check_in = ensure_utc(res.check_in)
                guest_check_out = ensure_utc(res.check_out)

                # Overlap if (start <= other_end) and (end >= other_start)
                if (check_in <= guest_check_out) and (check_out >= guest_check_in):
                    raise ValueError(
                        f"Guest {guest.guest_id} already has a reservation "
                        f"for room {selected_room_id} from {guest_check_in} to {guest_check_out}."
                    )

        # 5) Create the reservation. 
        #    If your test wants the final status to be "confirmed", set it so here.
        new_reservation = ReservationSchema(
            guest_id=guest_id,
            room_id=selected_room_id,
            check_in=check_in,
            check_out=check_out,
            status="confirmed"   # or "booked" depending on your logic
        )
        created_reservation = await self.reservation_repo.create_reservation(new_reservation)
        return created_reservation

    async def get_reservations_for_guest(self, guest_id) -> List[ReservationSchema]:
        """Get all reservations for a guest, handling both string UUIDs and UUID objects."""
        # Ensure guest_id is a string for SQLite compatibility
        if isinstance(guest_id, UUID):
            guest_id = str(guest_id)
            
        return await self.reservation_repo.list_reservations_by_guest_id(guest_id)

    async def modify_reservation(
        self,
        reservation_id: int,
        check_in: Optional[datetime] = None,
        check_out: Optional[datetime] = None,
        room_type: Optional[str] = None
    ) -> ReservationSchema:

        existing_reservation = await self.reservation_repo.get_reservation_by_id(reservation_id)
        if not existing_reservation:
            raise ValueError(f"Reservation with id={reservation_id} not found.")

        current_check_in = ensure_utc(existing_reservation.check_in)
        current_check_out = ensure_utc(existing_reservation.check_out)
        current_room_id = existing_reservation.room_id
        guest_id = existing_reservation.guest_id

        # Ensure guest_id is a string for SQLite compatibility
        if isinstance(guest_id, UUID):
            guest_id = str(guest_id)

        # If room_type changes, pick a new room
        new_room_id = current_room_id
        if room_type:
            room_type = room_type.lower()
            if room_type == "single":
                possible_rooms = range(101, 111)
            elif room_type == "double":
                possible_rooms = range(111, 121)
            elif room_type == "suite":
                possible_rooms = range(121, 131)
            else:
                raise ValueError(f"Invalid room type '{room_type}'")
            new_room_id = random.choice(list(possible_rooms))

        # Figure out final check_in/out
        new_check_in = current_check_in
        if check_in:
            new_check_in = ensure_utc(check_in)
        new_check_out = current_check_out
        if check_out:
            new_check_out = ensure_utc(check_out)

        if new_check_out <= new_check_in:
            raise ValueError("Check-out date must be after check-in date.")

        room_changed = (new_room_id != current_room_id)
        date_changed = (new_check_in != current_check_in or new_check_out != current_check_out)
        if room_changed or date_changed:
            # check for overlap on new room
            existing_res_for_guest = await self.reservation_repo.list_reservations_by_guest_id(guest_id)
            for res in existing_res_for_guest:
                if res.reservation_id == reservation_id:
                    continue
                if res.room_id == new_room_id:
                    guest_check_in = ensure_utc(res.check_in)
                    guest_check_out = ensure_utc(res.check_out)
                    if (new_check_in <= guest_check_out) and (new_check_out >= guest_check_in):
                        raise ValueError(
                            f"Guest {guest_id} already has a reservation for room {new_room_id} "
                            f"overlapping ({guest_check_in} to {guest_check_out})."
                        )

        updated = await self.reservation_repo.update_reservation(
            reservation_id=reservation_id,
            new_check_in=new_check_in,
            new_check_out=new_check_out,
            new_room_id=new_room_id
        )
        return updated

    async def cancel_reservation(self, reservation_id: int) -> bool:
        """
        Cancels (deletes) an existing reservation. Return True if deleted.
        """
        success = await self.reservation_repo.delete_reservation(reservation_id)
        if not success:
            raise ValueError(f"Reservation with id={reservation_id} not found")
        print(f"\nReservation with id={reservation_id} was cancelled successfully.\n")
        return True