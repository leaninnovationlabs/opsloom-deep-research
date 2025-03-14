Below is a roadmap for exposing a clean, maintainable API to your Pydantic AI agent and to your FastAPI consumers, without overcomplicating the design. We’ll reference common Python layering approaches, your existing **repository** pattern, and some helpful guidance from the [Pydantic AI docs](https://ai.pydantic.dev/).

---

## 1. Why Consider a Service Layer?

Right now, you have **Repositories** that directly interface with your database tables. That’s perfect for **low-level CRUD**. But a **Service Layer** adds a dedicated spot to place:

1. **Business logic** that’s more than simple CRUD, e.g., “Check if the room is available before booking,” “Calculate partial refunds,” “Send notifications on reservation changes,” etc.
2. **Complex orchestrations** that might span multiple repositories (e.g., creating a guest and a reservation in a single transaction).
3. **Validation, logging, or external API calls** that go beyond pure database interactions.

So, instead of exposing the repositories *directly* to the agent or your routes, you typically create **service methods** with a narrower, well-documented interface. Each service method calls the necessary repositories under the hood.

---

## 2. Folder/Module Structure

A commonly recommended structure:

```
backend/
├── routes/
│   ├── __init__.py
│   ├── room_routes.py
│   ├── guest_routes.py
│   └── reservation_routes.py
├── services/
│   ├── __init__.py
│   ├── room_service.py
│   ├── guest_service.py
│   └── reservation_service.py
├── db/
│   ├── models.py
│   └── repositories/
│       ├── __init__.py
│       ├── room.py
│       ├── guest.py
│       └── reservation.py
├── schemas/
│   ├── __init__.py
│   ├── room.py
│   ├── guest.py
│   └── reservation.py
└── main.py
```

**Key points**:

- **repositories/** remain small, single-entity CRUD classes.  
- **services/** combine or orchestrate repository calls and handle domain logic.  
- **routes/** are your FastAPI endpoints, each file typically matches one “resource” or domain area.

---

## 3. Exposing a Clear API to the Agent

### 3.1 Why Not Expose Repositories Directly?

- Repositories return raw DB entities or Pydantic schemas (and do minimal validation or logic).
- The AI agent might need “higher-level” actions, e.g., “Book a room for a given guest,” “Cancel a reservation and notify staff,” etc. This is not pure CRUD. 
- By exposing these domain-level methods in a **service** layer, you create a more “AI-friendly” interface—straightforward, documented, with fewer steps required to accomplish a domain-relevant task.

### 3.2 Defining an Agent-Facing API

With [Pydantic AI](https://ai.pydantic.dev/), you typically define “actions” or “methods” the agent can call. Each action can map to a **service method** rather than a raw repository method. For instance:

```python
from pydantic_ai import Action

class BookRoomAction(Action):
    """Book a room for the given guest."""
    guest_id: int
    room_type: str
    check_in: datetime
    check_out: datetime

    async def run(self) -> dict:
        # call your service
        reservation = await room_service.book_room_for_guest(
            guest_id=self.guest_id,
            room_type=self.room_type,
            check_in=self.check_in,
            check_out=self.check_out,
        )
        # return final result in a simple dictionary
        return reservation.dict()
```

- This `Action` calls a service method like `book_room_for_guest(...)` which you’d define in `services/room_service.py`. 
- The service method orchestrates checking availability, creating a reservation, possibly logging an audit, etc.
- This ensures the agent has a **clean, single-call** method for “Book a room,” instead of doing “List rooms by type,” “Check availability,” “Create reservation,” etc. step by step.

Pydantic AI will handle user questions or instructions, and your code decides which `Action` to invoke, passing validated arguments.

---

## 4. Example Service Layer

Below is a conceptual example in `services/room_service.py`. This is *not* exact code, just an illustration:

```python
# backend/services/room_service.py

from datetime import datetime
from backend.db.repositories.room import RoomRepository
from backend.db.repositories.reservation import ReservationRepository
from backend.schemas.reservation import ReservationSchema
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)

class RoomService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.room_repo = RoomRepository(db)
        self.reservation_repo = ReservationRepository(db)

    async def book_room_for_guest(
        self, guest_id: int, room_type: str, check_in: datetime, check_out: datetime
    ) -> ReservationSchema:
        """
        1) Find an available room of given type
        2) Create a reservation for that guest
        """
        # Step 1: find an available room
        available_rooms = await self.room_repo.list_available_rooms_by_type(room_type)
        if not available_rooms:
            raise ValueError(f"No {room_type} rooms available.")

        first_room = available_rooms[0]  # pick the first available
        # Step 2: create a reservation
        new_reservation = ReservationSchema(
            guest_id=guest_id,
            room_id=first_room.room_id,
            check_in=check_in,
            check_out=check_out,
            status="booked",
        )
        result = await self.reservation_repo.create_reservation(new_reservation)
        logger.info(
            "Booked room_id=%s for guest_id=%s from %s to %s",
            first_room.room_id, guest_id, check_in, check_out
        )
        return result
```

**Now** your Pydantic AI `Action` can do:

```python
from pydantic_ai import Action
from backend.services.room_service import RoomService

class BookRoomAction(Action):
    guest_id: int
    room_type: str
    check_in: datetime
    check_out: datetime

    async def run(self) -> dict:
        # you'll need access to the db somehow, e.g. a global or injected session
        service = RoomService(db=some_async_session)
        reservation = await service.book_room_for_guest(
            self.guest_id,
            self.room_type,
            self.check_in,
            self.check_out,
        )
        return reservation.model_dump()  # or .dict()
```

Now the agent has a single method `BookRoomAction` that handles all the steps. The user just says “Book me a suite for tomorrow,” and your agent code orchestrates everything behind the scenes.

---

## 5. FastAPI Routes

You mentioned you’ll have endpoints in **`backend/routes/`**. Typically:

- They’ll call your **service** methods as well.  
- They may not necessarily call the same code as the AI agent, or they might share it.  
- Example:

```python
# backend/routes/room_routes.py

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.room_service import RoomService
from backend.db.dependencies import get_db_session  # e.g. a standard FastAPI dependency

router = APIRouter()

@router.post("/book_room")
async def book_room(
    guest_id: int,
    room_type: str,
    check_in: datetime,
    check_out: datetime,
    db: AsyncSession = Depends(get_db_session)
):
    service = RoomService(db)
    reservation = await service.book_room_for_guest(
        guest_id, room_type, check_in, check_out
    )
    return reservation
```

**Note**: The same “book_room_for_guest” logic is used by both your AI agent (via `Action`) *and* your direct REST endpoint.

---

## 6. Minimizing Redundancy Between Schema & Model

You asked, “Is it possible to combine the schema and model with decorators or some approach so that we use the SQLAlchemy model with database stuff and the same model everywhere else?”

### 6.1 Why Typically We Keep Them Separate
- SQLAlchemy **models**: have DB-level concerns (table name, column definitions, relationships).
- Pydantic **schemas**: are about I/O validation, and can have additional constraints, different field names, etc.

### 6.2 Using **Pydantic’s `model_validate`** / `from_orm` Approach
You’re already using `RoomSchema.model_validate(...)` to convert directly from a SQLAlchemy model instance to a schema. That helps reduce a lot of the “manual mapping.”

### 6.3 If You Really Want to Merge
Some folks use **[sqlalchemy2-stubs + pydantic-sqlalchemy packages](https://pydantic-docs.helpmanual.io/usage/models/#orm-mode)** or tools like **[SQLModel](https://github.com/tiangolo/sqlmodel)** which unify the Pydantic and SQLAlchemy layers.  

However, be aware that merging your DB model and Pydantic model can complicate migrations or lead to leaky abstractions. The recommended approach from the Pydantic (and often from SQLAlchemy) community is to **keep them separate** but use “automatic conversions” (like `.model_validate(...)`) to reduce boilerplate.

---

## 7. Putting It All Together

1. **Keep** your **Repository** classes for raw DB operations.  
2. **Add** a **Service Layer** that orchestrates multi-step domain logic or calls multiple repositories.  
3. **Use** Pydantic AI’s **Actions** or custom endpoints to call those service methods:
   - The AI agent sees a small set of domain-level methods (e.g., “book room,” “cancel reservation,” “check availability”), not the entire DB.  
4. **Expose** REST endpoints in **`routes/`** that also call the same service methods, so your domain logic is DRY.  
5. **Avoid** merging your SQLAlchemy models and Pydantic schemas entirely. Using `model_validate()` or `from_orm=True` is typically enough to reduce redundancy, while preserving clear separation of DB concerns vs. input/output validation concerns.

---

## 8. Final Advice

- **Yes**, a **service layer** is valuable if you want a well-structured and safe API for both your normal FastAPI routes and your AI agent.
- **Document** each service method or “action” with clear docstrings (what it does, what exceptions it raises). The AI agent (and your colleagues) then see a straightforward set of domain-specific methods.
- For **Pydantic AI** in particular:
  - Create an **`Agent`** with an array of `Actions`.
  - Each `Action` references exactly one service method or a group of related logic.
  - In your application code, you can define how to pass your DB session to those actions.  

Following this approach keeps your domain logic in one place (the service layer), your database logic in repositories, and your API/AI logic clearly at the top, each with minimal duplication.