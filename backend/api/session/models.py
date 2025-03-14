from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from uuid import UUID, uuid4
import datetime as dt

class UserSession(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(default="")
    assistant_id: UUID
    user_id: UUID
    account_id: UUID
    data: Optional[Dict] = Field(default=None)
    created_at: dt.datetime = Field(default_factory=dt.datetime.now)
    class Config:
        arbitrary_types_allowed = True

class SessionList(BaseModel):
    list: List[UserSession]

class SessionRequest(BaseModel):
    assistant_id: UUID

class SessionResponse(BaseModel):
    session: UserSession