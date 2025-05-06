import logging
from typing import AsyncIterator, Dict, Any, List
import uuid
import json # Import json for potential data serialization

from backend.api.assistant.base_assistant_gateway import BaseAssistantGateway
from backend.api.chat.models import ChatRequest, OpsLoomMessageChunk
from backend.api.chat.repository import ChatRepository
from backend.api.session.repository import SessionRepository
from backend.util.auth_utils import TokenData

# Import the compiled LangGraph app (plan-execute-replan version)
from .graph import app
from .state import PlanExecute
# Import the synthesizer chain components from nodes.py
from .nodes import SYNTHESIS_PROMPT, synthesis_llm, StrOutputParser 

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 

# Define the synthesizer chain here for use in the gateway
synthesizer = SYNTHESIS_PROMPT | synthesis_llm | StrOutputParser()

class DeepResearchGateway(BaseAssistantGateway):
    # Define slots based on dependencies passed in __init__
    __slots__ = ("chat_repo", "session_repo", "current_user", "langgraph_app")

    def __init__(
        self,
        message_gateway: ChatRepository,
        session_gateway: SessionRepository,
        current_user: TokenData = None,
        **kwargs
    ):
        """Initializes the gateway with necessary repositories and the LangGraph app."""
        self.chat_repo = message_gateway
        self.session_repo = session_gateway
        self.current_user = current_user
        self.langgraph_app = app # Use the imported compiled graph
        
        logger.info("DeepResearchGateway initialized with LangGraph app.")

    async def get_ai_response_stream(self, chat_request: ChatRequest) -> AsyncIterator[OpsLoomMessageChunk]:
        """
        Runs the plan-execute-replan graph using astream_events (v2)
        and streams only the final response token by token.
        """
        session_uuid = str(chat_request.session_id)
        user_query = chat_request.message.content

        initial_state: PlanExecute = {
            "input": user_query,
            "plan": [],
            "past_steps": [],
            "response": "",
            "step_count": 0
        }

        thread_id = str(uuid.uuid4()) # Use a unique ID for each request
        config = {
            "configurable": {"thread_id": thread_id},
            "recursion_limit": 60 # Ensure sufficient recursion depth
        }

        logger.info(f"Starting LangGraph astream_events run for input: {user_query[:50]}... Config: {config}")

        final_response_content = ""
        streamed_something = False
        synthesis_started = False

        try:
            async for event in self.langgraph_app.astream_events(initial_state, config=config, version="v2"):
                event_type = event["event"]
                node_name = event.get("name")
                
                # Only process the start of the final synthesis node
                if event_type == "on_chain_start" and node_name == "synthesize_final_response" and not synthesis_started:
                    synthesis_started = True # Prevent starting synthesis multiple times if node somehow restarts
                    logger.info(f"--- Final Synthesis Started (via {node_name} start event) ---")
                    event_data = event["data"]
                    
                    # Extract necessary data from the event's input state
                    current_state = event_data.get("input", {})
                    input_query = current_state.get("input")
                    past_steps_list = current_state.get("past_steps", [])

                    if not input_query:
                        logger.error("Could not extract 'input' from state for final synthesis")
                        yield OpsLoomMessageChunk(type="text", content="Error: Missing input for final synthesis.\n")
                        continue # Skip synthesis if input is missing

                    # Format past steps
                    formatted_past_steps = "\n\n".join([
                        f"Step: {task}\nResult: {result}"
                        for task, result in past_steps_list
                    ]) if past_steps_list else "No research results available."

                    # Now, stream the synthesizer directly
                    try:
                        async for chunk in synthesizer.astream({
                            "input": input_query,
                            "past_steps": formatted_past_steps
                        }):
                            if chunk: # Ensure we don't yield empty chunks
                                yield OpsLoomMessageChunk(type="text", content=chunk)
                                final_response_content += chunk
                                streamed_something = True
                        logger.info("Synthesizer streaming finished.")
                    except Exception as synth_error:
                         logger.error(f"Error during synthesizer streaming: {synth_error}", exc_info=True)
                         yield OpsLoomMessageChunk(type="text", content=f"Error during final synthesis: {str(synth_error)}\n")
                         # Continue to allow graph to finish, but response might be incomplete

                # Log other events minimally for debugging if needed
                # elif node_name != "synthesize_final_response";
                #    logger.debug(f"Graph Event: type='{event_type}', name='{node_name}'")

        except Exception as e:
            logger.error(f"Error during main graph streaming loop: {e}", exc_info=True)
            # Yield an error message only if synthesis hasn't already started/failed
            if not synthesis_started:
                 yield OpsLoomMessageChunk(type="text", content=f"Error: An error occurred before final synthesis: {str(e)}\n")
            return

        # --- Final Check --- 
        if not streamed_something:
             logger.warning("Graph finished, but no final response was streamed.")
             yield OpsLoomMessageChunk(type="text", content="Error: Research agent finished without producing a final response.\n")

        logger.info("Gateway get_ai_response_stream finished.")

    async def get_summary_title(self, chat_request: ChatRequest) -> str:
        """
        Generate a summary title based on the input query.
        """
        topic = chat_request.message.content
        return f"Deep Research Agent: {topic[:30]}..." 