from pydantic import BaseModel, Field
from typing import List, Union, Optional

class Plan(BaseModel):
    """Plan to follow in future"""
    steps: List[str] = Field(
        ..., 
        description="different steps to follow, should be in sorted order"
    )

class Response(BaseModel):
    """Response to user."""
    response: str

# Revert Act to a BaseModel, using Optional fields for the choice
class Act(BaseModel):
    """Action to perform. Either a plan or a response."""
    plan: Optional[Plan] = Field(default=None, description="The updated plan if further steps are needed.")
    response: Optional[Response] = Field(default=None, description="The final response if the objective is met.")

    # Add a validator maybe? Or rely on prompt instructions.
    # @root_validator(pre=True)
    # def check_one_action(cls, values):
    #     if values.get('plan') is not None and values.get('response') is not None:
    #         raise ValueError("Cannot have both plan and response")
    #     if values.get('plan') is None and values.get('response') is None:
    #         raise ValueError("Must have either plan or response")
    #     return values 