"""
seed account table

Revision ID: 993c8d5598f3
Revises: 005_505ad0942e84
Create Date: 2024-09-17 13:03:48.310054
"""

from typing import Sequence, Union
import uuid
import os
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session, sessionmaker

from sqlalchemy.dialects.postgresql import UUID

# Revision identifiers, used by Alembic
revision: str = "006_993c8d5598f3"
down_revision: Union[str, None] = "005_505ad0942e84"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# --- IMPORT your ORM + Pydantic models here ---
# Example paths (adjust to your actual code structure):
from backend.api.account.account_schema import AccountORM  # The SQLAlchemy model
from backend.api.account.models import root as root_account  # The Pydantic root

def upgrade():
    """Seed an account row using the Pydantic model + SQLAlchemy ORM."""

    print(f"Running seed with multitenant={os.getenv('multitenant', 'true')}")
    is_multitenant = os.getenv("multitenant", "true").lower() == "true"
    print(f"multitenant is: {is_multitenant} {os.getenv('multitenant')}")

    if not root_account.short_code:
        root_account.short_code = "default"

    # Acquire a synchronous Session for this migration
    bind = op.get_bind()
    session = Session(bind=bind)

    existing = session.get(AccountORM, root_account.account_id)
    if existing:
        print(f"Account {root_account.account_id} already exists; skipping insert.")
        session.close()
        return

    new_orm = AccountORM(
        account_id=root_account.account_id,
        short_code=root_account.short_code,
        name=root_account.name or "root account",
        email=root_account.email,
        password="scoobydoo",
        account_metadata=root_account.metadata,  
        root=True,
        protection="email",
    )

    session.add(new_orm)
    try:
        session.commit()
        print(f"Inserted account {root_account.account_id}")
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def downgrade():
    """Remove the seeded account + associated data (message, session, etc.)."""
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID

    bind = op.get_bind()
    session = Session(bind=bind)

    # 1) Delete message records
    # Using raw SQL text, or you could define a MessageORM if you want:
    stmt = sa.text(
        """
        DELETE FROM message 
         WHERE session_id IN (
           SELECT id FROM session WHERE account_id = :account_id
         )
        """
    ).bindparams(sa.bindparam("account_id", type_=PG_UUID(as_uuid=True)))
    session.execute(stmt.params(account_id=root_account.account_id))

    # 2) Delete session
    stmt = sa.text("DELETE FROM session WHERE account_id = :account_id") \
        .bindparams(sa.bindparam("account_id", type_=PG_UUID(as_uuid=True)))
    session.execute(stmt.params(account_id=root_account.account_id))

    # 3) Delete assistant
    stmt = sa.text("DELETE FROM assistant WHERE account_short_code = :account_short_code") \
        .bindparams(sa.bindparam("account_short_code"))
    session.execute(stmt.params(account_short_code=root_account.short_code))

    # 4) Delete kbase
    stmt = sa.text("DELETE FROM kbase WHERE account_short_code = :account_short_code") \
        .bindparams(sa.bindparam("account_short_code"))
    session.execute(stmt.params(account_short_code=root_account.short_code))

    # 5) Delete users
    stmt = sa.text("DELETE FROM users WHERE account_id = :account_id") \
        .bindparams(sa.bindparam("account_id", type_=PG_UUID(as_uuid=True)))
    session.execute(stmt.params(account_id=root_account.account_id))

    # 6) Finally, delete the seeded account itself
    # We can also do this via the ORM:
    account_to_delete = session.get(AccountORM, root_account.account_id)
    if account_to_delete:
        session.delete(account_to_delete)

    session.commit()
    session.close()
