"""add deep-research agent

Revision ID: 1a19a754eb8f
Revises: 95fce5bd97c2
Create Date: 2025-04-30 22:48:56.748531

"""
from typing import Sequence, Union
import uuid
import os

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

# Imports from backend/api/assistant
from backend.api.assistant.assistant_schema import AssistantORM
from backend.api.assistant.models import (
    Assistant,
    AssistantConfig,
    Metadata,
)

# revision identifiers, used by Alembic.
revision: str = '1a19a754eb8f'
down_revision: Union[str, None] = '95fce5bd97c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Define the UUID for the new assistant
DEEP_RESEARCH_ASSISTANT_ID = uuid.UUID("47d935ec-8602-4ab5-8100-779712c25062") 

def get_deep_research_assistant_data() -> Assistant:
    """
    Returns the Pydantic Assistant model for the Deep Research agent.
    """
    is_multitenant = os.getenv("multitenant", "true").lower() == "true"
    default_short_code = "lil" if is_multitenant else "default"
    
    return Assistant(
        id=DEEP_RESEARCH_ASSISTANT_ID,
        name="deep_research_agent",
        account_short_code=default_short_code,
        kbase_id=None, 
        config=AssistantConfig(
            provider="openai", # Or appropriate provider
            type="deep_research", 
            model="gpt-4o", # Or appropriate model
        ),
        system_prompts={
            "system": "You are a Deep Research Assistant. Your goal is to perform comprehensive research on topics provided by the user, utilizing available tools and knowledge sources."
        },
        assistant_metadata=Metadata(
            title="Deep Research Agent",
            description="Performs in-depth research and analysis.",
            icon="travel_explore", # Material icon name
            prompts=[
                "Research the market trends for electric vehicles in Europe.",
                "Provide a competitive analysis for SaaS accounting software.",
                "Summarize recent academic papers on quantum computing.",
            ],
            num_history_messages=5, # Default or specific number
        ),
    )

def upgrade() -> None:
    """Adds the Deep Research assistant to the assistant table."""
    print(f"Adding Deep Research assistant (ID: {DEEP_RESEARCH_ASSISTANT_ID})")
    assistant_data = get_deep_research_assistant_data()

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Check if the assistant already exists
        existing = session.get(AssistantORM, assistant_data.id)
        if existing:
            print(f"Assistant {assistant_data.id} already exists; skipping insert.")
            session.close()
            return

        # Convert Pydantic -> ORM
        new_assistant = AssistantORM(
            id=assistant_data.id,
            account_short_code=assistant_data.account_short_code,
            kbase_id=assistant_data.kbase_id,
            name=assistant_data.name,
            config=assistant_data.config.model_dump(),
            system_prompts=assistant_data.system_prompts,
            assistant_metadata=(
                assistant_data.assistant_metadata.model_dump()
                if assistant_data.assistant_metadata
                else None
            ),
            # Assuming 'active' defaults to True or handle as needed
            # active=True 
        )

        session.add(new_assistant)
        session.commit()
        print(f"Successfully inserted assistant {assistant_data.id}")

    except Exception as e:
        session.rollback()
        print(f"Error adding assistant {assistant_data.id}: {e}")
        raise e # Re-raise the exception to halt the migration on error
    finally:
        session.close()


def downgrade() -> None:
    """Removes the Deep Research assistant from the assistant table."""
    print(f"Removing Deep Research assistant (ID: {DEEP_RESEARCH_ASSISTANT_ID})")
    assistant_id = DEEP_RESEARCH_ASSISTANT_ID

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        # Find the assistant by ID
        existing = session.get(AssistantORM, assistant_id)
        
        if existing:
            session.delete(existing)
            session.commit()
            print(f"Successfully removed assistant {assistant_id}")
        else:
            print(f"Assistant {assistant_id} not found; skipping deletion.")

    except Exception as e:
        session.rollback()
        print(f"Error removing assistant {assistant_id}: {e}")
        raise e # Re-raise the exception to halt the migration on error
    finally:
        session.close()
