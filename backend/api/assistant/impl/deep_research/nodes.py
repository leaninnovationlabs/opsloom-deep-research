import asyncio
import logging
from typing import Literal, Dict, List

from langchain_openai import ChatOpenAI
from langgraph.graph import END 
from langchain_core.prompts import ChatPromptTemplate as CoreChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from .state import PlanExecute
from .models import Plan, Response 
from .prompts import PLANNER_PROMPT, REPLANNER_PROMPT
from .react_agent import agent_executor

logger = logging.getLogger(__name__)

# Max steps safety limit
MAX_STEPS = 15 #can also be set to a higher value

planner_llm = ChatOpenAI(model="gpt-4o", temperature=0) 
replanner_llm = ChatOpenAI(model="gpt-4o", temperature=0) 
synthesis_llm = ChatOpenAI(model="gpt-4o", temperature=0)

# Chains
planner = PLANNER_PROMPT | planner_llm.with_structured_output(Plan)
replanner = REPLANNER_PROMPT | replanner_llm.with_structured_output(Plan) 

# Define a prompt for the final synthesis step
SYNTHESIS_PROMPT = CoreChatPromptTemplate.from_template(
    """You are an expert research analyst. Synthesize the following research notes into a final comprehensive report answering the original objective.
Be clear, concise, and directly address the objective.

Original Objective: {input}

Research Notes (Executed Steps and Results):
{past_steps}

Final Report:"""
)

# Chain for synthesis
synthesizer = SYNTHESIS_PROMPT | synthesis_llm | StrOutputParser()

async def execute_step(state: PlanExecute) -> Dict[str, List | int]:
    """Executes the next step in the plan, updates plan state, increments step count."""
    logger.info("---EXECUTING STEP---")
    plan = state["plan"]
    step_count = state.get("step_count", 0)
    
    if not plan:
        logger.warning("execute_step called with empty plan.")
        return {"past_steps": [], "plan": [], "step_count": step_count} # Return current count
        
    task = plan[0]
    remaining_plan = plan[1:] 
    
    original_plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(state['plan']))
    task_formatted = f"""Original plan:\n{original_plan_str}\n\nExecute step: {task}"""
    logger.info(f"Executing task: {task} (Step #{step_count + 1})" )
    
    try:
        agent_response = await agent_executor.ainvoke(
            {"messages": [("user", task_formatted)]}
        )
        result_content = ""
        if isinstance(agent_response, dict) and "messages" in agent_response and agent_response["messages"]:
             last_message = agent_response["messages"][-1]
             result_content = getattr(last_message, 'content', str(last_message))
        else:
             result_content = str(agent_response)

        logger.info(f"Step result: {result_content[:100]}...")
        return {
            "past_steps": [(task, result_content)],
            "plan": remaining_plan, 
            "step_count": step_count + 1
        }
    except Exception as e:
        logger.error(f"Error executing step '{task}': {e}", exc_info=True)
        return {
            "past_steps": [(task, f"Error executing step: {e}")],
            "plan": remaining_plan, 
            "step_count": step_count + 1
        }

async def plan_step(state: PlanExecute) -> Dict[str, List | int]:
    """Generates the initial plan and initializes step count."""
    logger.info("---PLANNING INITIAL STEP---")
    try:
        plan_result = await planner.ainvoke({"messages": [("user", state["input"])]})
        logger.info(f"Initial plan raw output: {plan_result}")
        plan_steps = []
        if plan_result and plan_result.steps:
             plan_steps = plan_result.steps
             logger.info(f"Initial plan steps: {plan_steps}")
        else:
             logger.warning("Initial planner generated an empty plan.")
        # Initialize step count to 0
        return {"plan": plan_steps, "step_count": 0} 
    except Exception as e:
        logger.error(f"Error during initial planning: {e}", exc_info=True)
        return {"plan": [], "step_count": 0}

async def replan_step(state: PlanExecute) -> Dict[str, List]:
    """Updates the plan based on past steps. Returns updated plan or empty list."""
    logger.info("---REPLANNING STEP---")

    # If the plan is already empty, no need to replan.
    if not state["plan"]:
         logger.info("Plan is empty before replan, returning empty plan.")
         return {"plan": []} 

    formatted_past_steps = "\n".join([
        f"Step: {task}\nResult: {result}" 
        for task, result in state["past_steps"]
    ]) if state["past_steps"] else "No steps executed yet."
    
    state_for_replan = { 
        "input": state["input"], 
        "plan": state["plan"], 
        "past_steps": formatted_past_steps
    }
    logger.info(f"State for replan call: {state_for_replan}")

    try:
        # Replanner now returns Plan object directly
        plan_result: Plan = await replanner.ainvoke(state_for_replan)
        logger.info(f"Replanner LLM raw output: {plan_result}")
        
        if plan_result and plan_result.steps:
            new_plan = plan_result.steps
            logger.info(f"Replanner updated plan: {new_plan}")
            return {"plan": new_plan}
        else: # Handles case where LLM explicitly returns empty plan or invalid object
             logger.info("Replanner returned an empty or invalid plan, signalling completion.")
             return {"plan": []} 

    except Exception as e:
        logger.error(f"Error during replanning: {e}", exc_info=True)
        return {"plan": []} # Return empty plan on error

async def synthesize_final_response(state: PlanExecute) -> Dict[str, str]:
    """Node that signifies the start of the final synthesis step. 
    The actual synthesis and streaming happen in the gateway."""
    logger.info("---SYNTHESIS NODE START---")
    return {"response": "", "plan": []}

def should_end(state: PlanExecute) -> Literal["agent", "synthesize_final_response"]:
    """Determines whether to execute next step or synthesize, considering step limit."""
    logger.info("---CHECKING IF SHOULD END/SYNTHESIZE---")
    plan = state.get("plan")
    step_count = state.get("step_count", 0)

    # Check step count limit first
    if step_count >= MAX_STEPS:
         logger.warning(f"Step count limit ({MAX_STEPS}) reached. Forcing synthesis.")
         return "synthesize_final_response"
    # If plan is empty, synthesize
    elif not plan:
        logger.info("Plan is empty. Proceeding to synthesize final response.")
        return "synthesize_final_response"
    # Otherwise, continue executing the plan
    else:
        logger.info(f"Continuing to agent step ({step_count + 1}/{MAX_STEPS}). Remaining plan: {plan}")
        return "agent" 