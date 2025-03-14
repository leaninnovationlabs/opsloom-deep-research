"""
combined seed configurations for single and multi tenant modes

Revision ID: 007_combined_seed
Revises: 006_993c8d5598f3
Create Date: 2024-11-08 12:00:00.000000
"""

from typing import Sequence, Union
import uuid
import os
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

revision: str = "007_combined_seed"
down_revision: Union[str, None] = "006_993c8d5598f3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# -- Imports from your 'backend/api/assistant' folder.
# Adjust paths if necessary:
from backend.api.assistant.assistant_schema import Base, AssistantORM
from backend.api.assistant.models import (
    Assistant,
    AssistantConfig,
    Metadata,
)

# Detect multitenant from env
is_multitenant = os.getenv("multitenant", "true").lower() == "true"
default_short_code = "lil" if is_multitenant else "default"
print(f"default short code is: {default_short_code}")

def get_assistant_data() -> Assistant:
    """
    Return a Pydantic Assistant model pre-filled based on multitenant env.
    Replaces the old 'get_assistant_config' dictionary approach.
    """
    if is_multitenant:
        return Assistant(
            id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
            name="wheelcorp_policy_assistant",
            account_short_code=default_short_code,
            kbase_id=None,
            config=AssistantConfig(
                provider="openai",
                type="no_rag",
                model="gpt-4",
            ),
            system_prompts={
                "system": "You are WheelCorp Policy Assistant 3.0..."
            },
            assistant_metadata=Metadata(
                title="WheelCorp Policy Assistant",
                description="Your friendly guide to corporate compliance!",
                icon="policy",
                prompts=[
                    "How do I request sick leave?",
                    "What is the lunch break policy?",
                    "Can I work from home?",
                    "When are performance reviews?",
                ],
                num_history_messages=5,
            ),
        )
    else:
        return Assistant(
            id=uuid.UUID("12345678-1234-5678-1234-567812345678"),
            name="meat_counter_helper",
            account_short_code=default_short_code,
            kbase_id=None,
            config=AssistantConfig(
                provider="openai",
                type="no_rag",
                model="gpt-4",
            ),
            system_prompts={
                "system": (
                    "You are Meat Counter Assistant..."
                )
            },
            assistant_metadata=Metadata(
                title="Meat Counter Helper",
                description="Get simple answers about deli meats and slicing",
                icon="local_dining",
                prompts=[
                    "How long turkey breast stay fresh?",
                    "What thickness good for roast beef?",
                    "How many pound ham for 10 people?",
                ],
                num_history_messages=5,
            ),
        )


def upgrade():
    """Seed the 'assistant' table with a single record using the ORM + Pydantic."""
    print(f"Running seed with multitenant={os.getenv('multitenant', 'true')}")
    assistant_data = get_assistant_data()

    bind = op.get_bind()
    session = Session(bind=bind)

    # 1) Check if the assistant row already exists
    existing = session.get(AssistantORM, assistant_data.id)
    if existing:
        print(f"Assistant {assistant_data.id} already exists; skipping insert.")
        session.close()
        return

    # 2) Convert Pydantic -> ORM
    new_assistant = AssistantORM(
        id=assistant_data.id,
        account_short_code=assistant_data.account_short_code,
        kbase_id=assistant_data.kbase_id,
        name=assistant_data.name,
        config=assistant_data.config.model_dump(),  # store as dict in JSON column
        system_prompts=assistant_data.system_prompts,
        assistant_metadata=(
            assistant_data.assistant_metadata.model_dump()
            if assistant_data.assistant_metadata
            else None
        ),
    )

    session.add(new_assistant)
    try:
        session.commit()
        print(f"Inserted assistant {assistant_data.id}")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def downgrade():
    """
    Remove seeded data in correct order.
    """
    print(f"Running downgrade with multitenant={os.getenv('multitenant', 'true')}")
    assistant_data = get_assistant_data()
    assistant_id = assistant_data.id

    bind = op.get_bind()
    session = Session(bind=bind)

    # 1) Delete messages for sessions referencing this assistant
    stmt = sa.text(
        """
        DELETE FROM message
         WHERE session_id IN (
           SELECT id FROM session WHERE assistant_id = :assistant_id
         )
        """
    ).bindparams(sa.bindparam("assistant_id", type_=sa.dialects.postgresql.UUID(as_uuid=True)))
    session.execute(stmt.params(assistant_id=assistant_id))

    # 2) Delete sessions referencing this assistant
    stmt = sa.text("DELETE FROM session WHERE assistant_id = :assistant_id") \
        .bindparams(sa.bindparam("assistant_id", type_=sa.dialects.postgresql.UUID(as_uuid=True)))
    session.execute(stmt.params(assistant_id=assistant_id))

    # 3) Finally, delete the assistant row itself, via ORM or SQL
    existing = session.get(AssistantORM, assistant_id)
    if existing:
        session.delete(existing)

    session.commit()
    session.close()
