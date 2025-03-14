from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from uuid import UUID, uuid4

class Metadata(BaseModel):
    title: str
    description: str
    icon: str
    prompts: Optional[List[str]]
    num_history_messages: Optional[int] = 0


    class Config:
        alias = "assistant_metadata"
        from_attributes = True

class AssistantConfig(BaseModel):
    provider: str = Field(..., description="Provider of the assistant")
    type: str = Field(..., description="type of the assistant")
    model: str = Field(..., description="Model used by the assistant")
    table_name: Optional[str] = Field(default=None, description="Table name for the assistant")

class Assistant(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    account_short_code: Optional[str] = None
    kbase_id: Optional[UUID] = None
    config: AssistantConfig
    system_prompts: Dict[str, str]

    # The field name is 'assistant_metadata' to match the DB.
    # The alias is 'metadata' so your payload can still send "metadata": {...}
    assistant_metadata: Optional[Metadata] = Field(
        default=None,
        alias="metadata"
    )

    class Config:
        from_attributes = True         
        populate_by_name = True        
        by_alias = True                

class AssistantDeletion(BaseModel):
    id: UUID = Field(..., description="ID of the assistant to delete")

class AssistantList(BaseModel):
    assistants: List[Assistant] = Field(default=[], description="List of assistants")

    class Config:
        from_attributes = True
        