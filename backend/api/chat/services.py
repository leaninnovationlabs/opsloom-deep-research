import asyncio
import json
from typing import AsyncGenerator, Optional
import uuid
from uuid import UUID

from fastapi import HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.chat.models import (
    Message,
    MessagePair,
    ChatRequest,
    AIResponse,
    OpsLoomMessageChunk
)
from backend.api.chat.repository import ChatRepository, AgentMessagesRepository
from backend.api.chat.ai_response_service import AIResponseService
from backend.api.session.models import UserSession
from backend.api.session.repository import SessionRepository
from backend.api.assistant.repository import AssistantRepository
from backend.api.kbase.repository import KbaseRepository
from backend.util.logging import SetupLogging
from backend.util.auth_utils import TokenData

logger = SetupLogging()

class ChatService:
    """
    Manages chat requests and streaming LLM responses,
    with logic to skip new title generation if a session already has one.
    """
    __slots__ = (
        "db",
        "chat_repository",
        "agent_message_repository",
        "session_repository",
        "assistant_repository",
        "current_user",
        "kbase_repository",
        "retriever",
    )

    def __init__(self, db: AsyncSession, current_user: TokenData = None):
        self.db = db
        self.chat_repository = ChatRepository(db)
        self.agent_message_repository = AgentMessagesRepository(db)
        self.session_repository = SessionRepository(db)
        self.assistant_repository = AssistantRepository(db)
        self.kbase_repository = KbaseRepository(db)
        self.current_user = current_user
        self.retriever = None  # optional retrieval pipeline

    async def process_chat_request(
        self,
        request: ChatRequest,
        current_user: TokenData,
        background_tasks: BackgroundTasks
    ) -> AsyncGenerator[str, None]:
        """
        Orchestrates streaming from the LLM, stores final user+AI message pair (if applicable).
        Yields individual OpsLoomMessageChunk events received from the gateway.
        """
        # 1) Validate the session
        logger.info(f"Processing chat request for session: {request.session_id}")
        session = await self.validate_session(request.session_id, current_user)

        # 2) Convert assistant_id to a standard UUID if needed
        if not isinstance(session.assistant_id, UUID):
            assistant_id_uuid = UUID(str(session.assistant_id))
        else:
            assistant_id_uuid = session.assistant_id

        # 3) Initialize the AIResponseService
        ai_service = AIResponseService(
            db=self.db,
            chat_repo=self.chat_repository,
            agent_message_repo=self.agent_message_repository,
            current_user=current_user,
            retriever=self.retriever
        )
        await ai_service.initialize(assistant_id_uuid)

        # 4) Handle Title Generation (asynchronously)
        title_exists = await self.session_repository.check_session_title(session.id)
        title_future = None
        if not title_exists:
            logger.info("No existing title found, scheduling title generation.")
            title_future = asyncio.ensure_future(ai_service.get_summary_title(request))

        final_ai_content_for_db = "" # Accumulate TEXT content for DB storage
        accumulated_stream_content = "" # Accumulate text content for yielding
        message_id_for_db = None # Store the message ID for DB saving
        title_sent_in_stream = False # Track if title was sent

        try:
            # Stream directly from the AI service (which yields OpsLoomMessageChunk dicts)
            async for ops_chunk in ai_service.get_ai_response_stream(request):
                logger.debug(f"Received ops_chunk from gateway: {ops_chunk}")

                message_id_for_db = ops_chunk.get("message_id")
                current_content = ops_chunk.get("content", "")
                current_type = ops_chunk.get("type", "text")
                response_md = ops_chunk.get("response_metadata", {})

                current_blocks = [] # Reset blocks for the chunk to be yielded

                # OLD LOGIC for accumulating content and building blocks for yielding
                # Append chunk's text content into the final full response
                # nonlocal full_resp, title_sent, block_content, title_future
                # full_resp.content += content_str

                # # Construct a 'block_content' for JSON. Customize to your UI needs:
                # if chunk_type == "text":
                #     block_content = {
                #         "type": "text",
                #         "text": full_resp.content
                #     }
                # elif chunk_type == "table":
                #     block_content = {
                #         "type": "table",
                #         "data": content_str,
                #         "config": {
                #             "title": response_md.get("title", ""),
                #             "description": response_md.get("description", ""),
                #         }
                #     }
                # elif chunk_type == "dialog":
                #     block_content = {
                #         "type": "dialog",
                #         "content": content_str,
                #         "config": {
                #             "title": response_md.get("title", ""),
                #             "description": response_md.get("description", ""),
                #             "actions": response_md.get("actions", [])
                #         }
                #     }
                # elif chunk_type == "barchart":
                #     block_content = {
                #         "type": "barchart",
                #         "data": content_str,
                #         "config": {
                #             "title": response_md.get("title", ""),
                #             "description": response_md.get("description", ""),
                #             "xAxis": response_md.get("xAxis", ""),
                #             "yAxis": response_md.get("yAxis", ""),
                #             "explanation": response_md.get("explanation", ""),
                #         }
                #     }
                # else:
                #     block_content = {
                #         "type": chunk_type,
                #         "content": content_str
                #     }

                # # Build partial chunk_data to yield
                # chunk_data = {
                #     "message_id": str(full_resp.message_id),
                #     "assistant_id": str(assistant_id_uuid),
                #     "blocks": [block_content],
                # }

                # NEW LOGIC for accumulating content and building blocks for yielding
                # Accumulate content and build blocks for yielding
                if current_type == "text":
                    accumulated_stream_content += current_content
                    current_blocks = [{"type": "text", "text": accumulated_stream_content}] # Use ACCUMULATED content
                    final_ai_content_for_db = accumulated_stream_content # Keep DB content in sync
                elif current_type == "status":
                    current_blocks = [{"type": "status", "text": current_content}]
                    # Don't add status to final_ai_content_for_db
                elif current_type == "error":
                     current_blocks = [{"type": "error", "text": current_content}]
                     # Decide if/how errors affect final DB state - currently not added to content
                # Add handling for other specific block types (e.g., dialog) if they should be yielded
                # elif current_type == "dialog":
                #    current_blocks = [...] # Construct dialog block based on current_content/response_md
                else:
                    # Handle unexpected chunk types if necessary, maybe yield as simple text
                    logger.warning(f"Unhandled chunk type '{current_type}' in stream, yielding as simple text block.")
                    current_blocks = [{"type": "text", "text": current_content}]
                    # Decide if unhandled types should be accumulated for DB
                    # final_ai_content_for_db += current_content

                # Ensure blocks are never empty if we intend to yield something
                if not current_blocks:
                     logger.warning(f"Block construction resulted in empty list for chunk type '{current_type}'. Skipping yield for this chunk.")
                     continue # Skip yielding this chunk

                chunk_data_to_yield = {
                    "message_id": str(message_id_for_db or ""),
                    "assistant_id": str(assistant_id_uuid),
                    "blocks": current_blocks, # Use the blocks (potentially accumulated) built above
                    "type": current_type, # Keep original type info
                    "content": current_content, # Keep original content info
                    "response_metadata": response_md,
                    "name": ops_chunk.get("name"),
                    "id": ops_chunk.get("id")
                }

                # If title is ready, attach it to *this* chunk (only once)
                if not title_sent_in_stream and title_future and title_future.done():
                    try:
                        possible_title = title_future.result()
                        if possible_title:
                            logger.info(f"Attaching title to chunk: {possible_title}")
                            chunk_data_to_yield["title"] = possible_title
                            title_sent_in_stream = True # Mark as sent
                            # Add task to update DB title in background *once*
                            background_tasks.add_task(
                                self.session_repository.update_session_title,
                                session.id,
                                possible_title
                            )
                    except Exception as e:
                        logger.error(f"Error retrieving summary title for chunk: {str(e)}")
                        title_future = None # Don't try again in this stream

                # Yield each processed chunk as a JSON line
                logger.info(f"Yielding chunk_data JSON: {chunk_data_to_yield}")
                yield json.dumps(chunk_data_to_yield) + "\n"
                logger.debug("Successfully yielded chunk.")

        except Exception as e_stream:
            logger.error(f"Error during ChatService streaming loop: {e_stream}", exc_info=True)
            # Optionally yield an error chunk to the frontend
            yield json.dumps({
                "type": "error",
                "content": f"An error occurred: {str(e_stream)}",
                "message_id": str(message_id_for_db or uuid.uuid4()),
                "assistant_id": str(assistant_id_uuid),
                "blocks": [{"type": "error", "text": f"An error occurred: {str(e_stream)}"}]
            }) + "\n"
            # We might still want to save what we have up to the error point

        finally:
            logger.info("Exiting ChatService streaming loop.")
            # --- Store Final Message Pair --- outside the main try/except for stream errors
            try:
                # Use the final accumulated content/blocks for DB saving
                if not request.message.blocks:
                    request.message.blocks = [{"type": "text", "text": request.message.content or ""}]

                # Construct final AI message for DB based on final accumulated TEXT content
                if final_ai_content_for_db:
                    # Final blocks for DB should represent the complete text response
                    final_ai_blocks_for_db = [{"type": "text", "text": final_ai_content_for_db}]
                    logger.info(f"Preparing to save final message pair. Content start: {final_ai_content_for_db[:100]}... Final Blocks: {final_ai_blocks_for_db}")
                    final_ai_message = Message(
                        role="ai",
                        content=final_ai_content_for_db, # Final accumulated TEXT content
                        blocks=final_ai_blocks_for_db # Final block structure based on accumulated text
                    )
                    await self.store_message_pair(session, request, final_ai_message, message_id_for_db)
                    logger.info("Successfully saved final message pair.")
                else:
                     logger.warning("Final AI content for DB is empty. Skipping save.")

                # Handle title DB update if it wasn't done during streaming
                if not title_sent_in_stream and title_future:
                    if title_future.done():
                         try:
                             final_title = title_future.result()
                             if final_title:
                                 logger.info("Updating title in DB after stream finished.")
                                 # Ensure background task wasn't already added
                                 if not any(task.func == self.session_repository.update_session_title for task in background_tasks.tasks):
                                      background_tasks.add_task(
                                          self.session_repository.update_session_title,
                                          session.id,
                                          final_title
                                      )
                         except Exception as e_title:
                             logger.error(f"Error updating title after stream: {e_title}")
                    else:
                         logger.warning("Title generation future did not complete before stream end.")
                         # Optionally wait briefly or just log

            except Exception as e_final:
                 logger.error(f"Error during final message saving/title update: {e_final}", exc_info=True)
                 # Decide if this error needs to be propagated or just logged


    async def validate_session(self, session_id: str, current_user: TokenData) -> UserSession:
        """
        Load session, ensure it belongs to current_user.
        """
        session_uuid = UUID(session_id)
        user_session = await self.session_repository.get_user_session(session_uuid)
        if not user_session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Check permission
        if (
            str(current_user.user_id) != str(user_session.user_id)
            or str(current_user.account_id) != str(user_session.account_id)
        ):
            raise HTTPException(status_code=403, detail="Forbidden")

        return user_session

    async def store_message_pair(self, session: UserSession, request: ChatRequest, ai_message: Message, message_id: Optional[UUID] = None):
        """
        Store a single user+AI message pair in the DB, using provided message_id if available.
        """
        try:
            # Use provided message_id or generate a new one if None
            msg_id_to_use = message_id or uuid.uuid4()
            
            pair = MessagePair(
                user_message=request.message,
                ai_message=ai_message, # Use the fully formed AI message
                message_id=msg_id_to_use,
                user_id=session.user_id,
                account_id=session.account_id,
                session_id=session.id
            )
            saved_ok = await self.chat_repository.save_message_pair(pair)
            if not saved_ok:
                logger.error(f"Failed to save message pair for session {request.session_id}")
        except Exception as e:
            logger.error(
                f"Error storing message pair for session {request.session_id}: {str(e)}",
                exc_info=True
            )
            # Decide if this should raise or just be logged depending on requirements
            # raise

    async def get_messages(self, session_id: str, current_user: TokenData):
        """
        Validate session, then return all stored messages.
        """
        _ = await self.validate_session(session_id, current_user)
        return await self.chat_repository.get_messages(UUID(session_id))

    async def submit_feedback(self, feedback_req, current_user: TokenData):
        """
        Possibly verify user has rights to this message, etc.
        """
        # Ensure feedback_req has necessary attributes
        if not hasattr(feedback_req, 'message_id') or not hasattr(feedback_req, 'feedback'):
             raise HTTPException(status_code=400, detail="Invalid feedback request format")
        
        return await self.chat_repository.update_message_feedback(
            message_id=feedback_req.message_id,
            feedback=feedback_req.feedback
        )
