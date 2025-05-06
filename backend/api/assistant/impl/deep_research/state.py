import operator
from typing import Annotated, List, Tuple
from typing_extensions import TypedDict

class PlanExecute(TypedDict):
    """State for the plan-execute-replan agent."""
    input: str                 # Initial user query
    plan: List[str]            # List of steps to execute
    past_steps: Annotated[     # History of executed steps and their results
        List[Tuple[str, str]], 
        operator.add
    ]
    response: str              # Final response to the user
    step_count: int            # Counter for executed steps 