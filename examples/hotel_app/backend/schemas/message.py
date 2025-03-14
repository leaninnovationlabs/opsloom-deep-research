from pydantic import BaseModel
from typing import Optional

class MessageSchema(BaseModel):
    content: str
    role: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class MessagePairSchema(BaseModel):
    message_id: Optional[int] = None
    guest_id: str
    session_id: str
    user_message: MessageSchema
    ai_message: MessageSchema
    
    class Config:
        from_attributes = True