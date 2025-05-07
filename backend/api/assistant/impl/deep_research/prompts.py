from langchain_core.prompts import ChatPromptTemplate

PLANNER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a research agent working in May 2025. For the given objective, come up with a simple step by step plan. \
This plan should involve individual tasks, that if executed correctly will yield the correct answer. Do not add any superfluous steps. The result of the final step should be the final answer. Make sure that each step has all the information needed - do not skip steps. At the end use the info collected to give the final answer to the main question containing the facts.""",
        ),
        ("placeholder", "{messages}"),
    ]
)

REPLANNER_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert assistant responsible for refining a research plan.
Analyze the original objective, the remaining plan steps, and the results of previously executed steps.

Original Objective: {input}
Remaining Plan: {plan}
Executed Steps and Results:
{past_steps}

Based on the results and remaining plan, determine if the *current remaining plan* is sufficient or needs refinement.
- If the remaining plan is good and contains the necessary next steps, output the *exact same remaining plan*. 
- If the remaining plan needs adjustment (e.g., steps are too vague, missing steps, can be combined), output the *new, refined plan* containing only the necessary future steps.
- If *no more steps* are needed based on the results achieved so far, output an *empty plan* (e.g., {{"plan": {{"steps": []}}}}).

Respond using the 'Act' tool, populating the 'plan' field with the updated or empty list of steps."""
) 

# Define a prompt for the final synthesis step
SYNTHESIS_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert research analyst. Synthesize the following research notes into a final comprehensive report answering the original objective.
Be clear, concise, and directly address the objective.

Original Objective: {input}

Research Notes (Executed Steps and Results):
{past_steps}

Final Report:"""
)