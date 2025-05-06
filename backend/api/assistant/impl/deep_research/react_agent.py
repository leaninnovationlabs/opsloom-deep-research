from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# System prompt for the ReAct agent that executes individual steps
# This could be customized further if needed
STEP_EXECUTOR_SYSTEM_PROMPT = "You are a helpful assistant. You have access to a search tool." 

# Initialize LLM and Tools (ensure API keys are set in environment)
# Consider making model name configurable
llm = ChatOpenAI(model="gpt-4o", temperature=0) 
tools = [TavilySearchResults(max_results=3)] # Reduced max_results for efficiency

# Create the ReAct agent executor
agent_executor = create_react_agent(
    llm,
    tools,
    # messages_modifier=STEP_EXECUTOR_SYSTEM_PROMPT # Note: 'state_modifier' in your example is likely 'messages_modifier'
    # If using older langgraph, might be checkpointer=... for system prompt
) 