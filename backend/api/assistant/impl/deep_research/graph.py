import json
import os
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from .state import PlanExecute
from .nodes import plan_step, execute_step, replan_step, should_end, synthesize_final_response

# --- Function to save graph JSON for LangGraph Studio --- 
def save_graph_json(graph_builder, filename="graph.json"):
    """Saves the graph structure as JSON for visualization."""
    try:
        # Draw from the StateGraph instance before compiling
        graph_json = graph_builder.draw_json() 
        filepath = os.path.join(os.path.dirname(__file__), filename)
        with open(filepath, 'w') as f:
            json.dump(graph_json, f, indent=2)
        print(f"Saved graph structure to {filepath}")
    except AttributeError:
        # This error occurs if draw_json doesn't exist on the builder
        print(f"Info: Couldn't find .draw_json() method on the graph builder. Skipping graph.json save.") 
    except Exception as e:
        print(f"Error saving graph JSON: {e}")

# Define the workflow
workflow_builder = StateGraph(PlanExecute)

# Add nodes
workflow_builder.add_node("planner", plan_step)
workflow_builder.add_node("agent", execute_step)
workflow_builder.add_node("replan", replan_step)
workflow_builder.add_node("synthesize_final_response", synthesize_final_response)

# Define edges
workflow_builder.add_edge(START, "planner")
workflow_builder.add_edge("planner", "agent")
workflow_builder.add_edge("agent", "replan")
workflow_builder.add_conditional_edges(
    "replan",
    should_end, 
    # Define paths for the conditions
    {
        "agent": "agent", # If should_end returns "agent", go back to agent node
        "synthesize_final_response": "synthesize_final_response" # If should_end returns "synthesize_final_response", go to synthesize_final_response node
    }
)

# Add edge from synthesize_final_response node to END
workflow_builder.add_edge("synthesize_final_response", END)

print("Skipping save_graph_json call during startup.") # Add print statement for confirmation

# Compile the graph with a checkpointer
checkpointer = MemorySaver()
app = workflow_builder.compile(checkpointer=checkpointer) 