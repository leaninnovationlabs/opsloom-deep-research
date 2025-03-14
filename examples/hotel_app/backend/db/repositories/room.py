from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.schemas.room import RoomSchema
from backend.db.models import Room
from datetime import datetime

class RoomRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_rooms(self) -> list[RoomSchema]:
        """
        Fetch all rooms from the database and return them
        as a list of RoomSchema.
        """
        result = await self.db.execute(select(Room))
        rows = result.scalars().all()

        room_schemas = [RoomSchema.model_validate(r) for r in rows]

        return room_schemas

    async def list_rooms_by_type(self, room_type: str) -> list[RoomSchema]:
        """
        Fetch rooms of a specific type from the database
        and return them as a list of RoomSchema.
        """
        result = await self.db.execute(select(Room).where(Room.room_type == room_type))
        rows = result.scalars().all()

        room_schemas = [RoomSchema.model_validate(r) for r in rows]

        return room_schemas
    
    async def get_room_by_room_id(self, room_id: int) -> RoomSchema:
        """
        Fetch a room by its room number from the database
        and return it as a RoomSchema.
        """
        result = await self.db.execute(select(Room).where(Room.room_id == room_id))
        row = result.scalar_one_or_none()

        if row is None:
            raise ValueError(f"No room found with room_id {room_id}")
        
        return RoomSchema.model_validate(row)
    
    async def list_available_rooms(self, start_date: datetime, end_date: datetime) -> list[RoomSchema]:
        """
        Fetch available rooms for a specific date range.
        This is a simplified implementation that just returns all rooms.
        In a real application, you would check for overlapping reservations.
        """
        # For now, just return all rooms as available
        return await self.list_rooms()