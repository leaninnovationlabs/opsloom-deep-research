from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
import os
from dotenv import load_dotenv
load_dotenv()

base_url = os.getenv("EXTERNAL_API_URL", "http://localhost:8081")

class ActionURLSchema(BaseModel):
    """Defines standardized URLs for different action types"""
    BASE_URL: str = base_url
    @classmethod
    def get_reservation_create_url(cls) -> str:
        """URL for creating a new reservation"""
        return f"{base_url}/reservations"
    
    @classmethod
    def get_reservation_modify_url(cls, reservation_id: int) -> str:
        """URL for modifying an existing reservation"""
        return f"{base_url}/reservations/{reservation_id}"
    
    @classmethod
    def get_reservation_cancel_url(cls, reservation_id: int) -> str:
        """URL for canceling a reservation"""
        return f"{base_url}/reservations/{reservation_id}"
    
    @classmethod
    def get_service_order_url(cls) -> str:
        """URL for service orders"""
        return f"{base_url}/serviceorders"

class ServiceSchema(BaseModel):
    service_id: int
    name: Literal[
        "room service", 
        "room service with hot meal", 
        "wake up call", 
        "late check in", 
        "hot water", 
        "electricity",
        "tour in local waste treatment facility", 
        "unstained towel", 
        "supervised visit", 
        "phone use"
    ]
    description: str
    price: float
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ServiceOrderSchema(BaseModel):
    order_id: Optional[int] = None
    reservation_id: int
    service_id: int
    quantity: int = 1
    status: Literal["pending", "completed", "cancelled"]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GuestSchema(BaseModel):
    guest_id: Optional[UUID] = None
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReservationSchema(BaseModel):
    reservation_id: Optional[int] = None
    guest_id: UUID
    room_id: Optional[int] = None
    check_in: datetime
    check_out: datetime
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreateReservationRequest(BaseModel):
    guest_id: UUID
    full_name: str
    email: str
    room_type: str
    check_in: datetime
    check_out: datetime

    model_config = ConfigDict(
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )
