from pydantic import BaseModel
from uuid import UUID

class SessionSchema(BaseModel):
    session_id: str = None
    guest_id: str

    class Config:
        from_attributes = True