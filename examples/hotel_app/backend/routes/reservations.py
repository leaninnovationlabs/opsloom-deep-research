from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from uuid import UUID
from backend.db.session import get_db_session
from backend.schemas.reservation import ReservationSchema
from backend.schemas.guest import GuestSchema
from backend.services.reservation import ReservationService

from pydantic import BaseModel


router = APIRouter()

# Request body models for creating or updating a reservation
class CreateReservationRequest(BaseModel):
    guest_id: str
    full_name: str
    email: str
    room_type: str
    check_in: datetime
    check_out: datetime

class UpdateReservationRequest(BaseModel):
    check_in: Optional[str] = None
    check_out: Optional[str] = None
    room_type: Optional[str] = None

@router.get("/reservations/{guest_id}", response_model=List[ReservationSchema])
async def get_reservations_for_guest(
    guest_id: UUID, 
    db: AsyncSession = Depends(get_db_session)
) -> List[ReservationSchema]:
    """
    Retrieve all reservations for a given guest_id.
    """
    reservation_service = ReservationService(db=db)
    # Convert UUID to string for SQLite compatibility
    guest_id_str = str(guest_id)
    return await reservation_service.get_reservations_for_guest(guest_id_str)


@router.post("/reservations", response_model=ReservationSchema)
async def create_reservation(
    req: CreateReservationRequest,
    db: AsyncSession = Depends(get_db_session)
) -> ReservationSchema:
    """
    Create a new reservation for a given guest, specifying room_type, check_in, check_out.
    """
    print(f"Creating reservation for guest {req.guest_id}")
    reservation_service = ReservationService(db=db)
    
    # Construct a GuestSchema from request data
    guest = GuestSchema(
        guest_id=str(req.guest_id),  # Convert UUID to string for SQLite
        full_name=req.full_name,
        email=req.email
    )
    
    try:
        new_res = await reservation_service.create_reservation(
            guest=guest,
            room_type=req.room_type,
            check_in=req.check_in,
            check_out=req.check_out
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    
    return new_res


@router.patch("/reservations/{reservation_id}", response_model=ReservationSchema)
async def modify_reservation(
    reservation_id: int,
    req: UpdateReservationRequest,
    db: AsyncSession = Depends(get_db_session)
) -> ReservationSchema:
    """
    Partially update an existing reservation's check_in, check_out, or room_type.
    """
    # Check that at least one field is provided with a value
    if req.check_in is None and req.check_out is None and req.room_type is None:
        raise HTTPException(status_code=400, detail="At least one field must be provided to update")
    
    # Parse ISO strings to datetime objects if present
    check_in_datetime = None
    if req.check_in:
        try:
            check_in_datetime = datetime.fromisoformat(req.check_in)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid check_in date format")
    
    check_out_datetime = None
    if req.check_out:
        try:
            check_out_datetime = datetime.fromisoformat(req.check_out)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid check_out date format")
    
    reservation_service = ReservationService(db=db)
    try:
        updated_res = await reservation_service.modify_reservation(
            reservation_id=reservation_id,
            check_in=check_in_datetime,
            check_out=check_out_datetime,
            room_type=req.room_type
        )
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    
    return updated_res

@router.delete("/reservations/{reservation_id}")
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Cancel (delete) an existing reservation by its reservation_id.
    """
    reservation_service = ReservationService(db=db)
    try:
        await reservation_service.cancel_reservation(reservation_id)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    return {"detail": f"Reservation {reservation_id} successfully cancelled"}