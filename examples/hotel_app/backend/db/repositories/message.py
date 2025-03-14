from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.schemas.message import MessageSchema, MessagePairSchema
from backend.db.models import MessagePair

class MessageRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_message(self, message: MessagePairSchema) -> MessagePairSchema:
        """
        Insert a new MessagePair row into the DB and return the created row as MessagePairSchema.
        """
        # Convert UUID to string for SQLite compatibility
        guest_id = str(message.guest_id) if isinstance(message.guest_id, UUID) else message.guest_id
        session_id = str(message.session_id) if isinstance(message.session_id, UUID) else message.session_id
        
        new_message_pair = MessagePair(
            guest_id=guest_id,
            session_id=session_id,
            user_message=message.user_message.content,
            ai_message=message.ai_message.content
        )

        self.db.add(new_message_pair)
        await self.db.commit()
        await self.db.refresh(new_message_pair)

        # Convert back to MessagePairSchema
        return MessagePairSchema(
            message_id=new_message_pair.message_id,
            guest_id=new_message_pair.guest_id,
            session_id=new_message_pair.session_id,
            user_message=MessageSchema(
                content=new_message_pair.user_message, 
                role="user",
            ),
            ai_message=MessageSchema(
                content=new_message_pair.ai_message, 
                role="assistant",
            )
        )

    async def list_messages(self) -> list[MessagePairSchema]:
        """
        Return all messages as a list of MessagePairSchema
        """
        result = await self.db.execute(select(MessagePair))
        rows = result.scalars().all()
        return [
            MessagePairSchema(
                message_id=row.message_id,
                guest_id=row.guest_id,
                session_id=row.session_id,
                user_message=MessageSchema(content=row.user_message, role="user"),
                ai_message=MessageSchema(content=row.ai_message, role="assistant"),
            )
            for row in rows
        ]

    async def get_messages_by_session_id(self, session_id: str | UUID) -> list[MessagePairSchema]:
        """
        Return all messages for the given session UUID.
        """
        # Convert UUID to string for SQLite compatibility
        session_id_str = str(session_id) if isinstance(session_id, UUID) else session_id
        
        result = await self.db.execute(
            select(MessagePair).where(MessagePair.session_id == session_id_str)
        )
        rows = result.scalars().all()
        return [
            MessagePairSchema(
                message_id=row.message_id,
                guest_id=row.guest_id,
                session_id=row.session_id,
                user_message=MessageSchema(content=row.user_message, role="user"),
                ai_message=MessageSchema(content=row.ai_message, role="assistant"),
            )
            for row in rows
        ]

    async def delete_messages_by_session_id(self, session_id: str | UUID) -> bool:
        """
        Delete all messages associated with the given session UUID.
        """
        # Convert UUID to string for SQLite compatibility
        session_id_str = str(session_id) if isinstance(session_id, UUID) else session_id
        
        result = await self.db.execute(
            select(MessagePair).where(MessagePair.session_id == session_id_str)
        )
        rows = result.scalars().all()

        for row in rows:
            await self.db.delete(row)
        await self.db.commit()
        return True