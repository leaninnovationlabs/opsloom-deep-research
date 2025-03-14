from pydantic import BaseModel
from datetime import datetime
from typing import Literal, Optional

class ReservationSchema(BaseModel):
    reservation_id: Optional[int] = None
    guest_id: str
    room_id: int
    check_in: datetime
    check_out: datetime

    # Adjust statuses as you want
    status: Literal["booked", "confirmed", "cancelled", "available"] = "booked"

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
