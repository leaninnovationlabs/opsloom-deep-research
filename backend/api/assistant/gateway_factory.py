import os
from backend.api.assistant.base_assistant_gateway import BaseAssistantGateway
from backend.api.assistant.impl.rag_ag import RagAssistant
from backend.api.assistant.impl.norag_ag import NoRagAssistant
from backend.api.assistant.impl.agent.agent_gateway import AgentGateway
from backend.api.assistant.impl.text_to_sql_ag import TextToSQL
from backend.api.assistant.impl.deep_research.deep_research_gateway import DeepResearchGateway
from backend.api.kbase.models import KnowledgeBase
from backend.api.assistant.models import Assistant
from backend.api.chat.repository import ChatRepository, AgentMessagesRepository
from backend.api.session.repository import SessionRepository
from backend.api.kbase.pgvectorstore import PostgresVectorStore
from backend.util.auth_utils import TokenData

class LLMGatewayFactory:
    __slots__ = ()
    @staticmethod
    def create_llm_gateway(
        assistant_type: "str",
        knowledge_base: KnowledgeBase,
        assistant: Assistant,
        message_gateway: ChatRepository,
        agent_message_gateway: AgentMessagesRepository,
        session_gateway: SessionRepository,
        vector_store: PostgresVectorStore,
        current_user: TokenData = None
    ) -> BaseAssistantGateway:
        if assistant_type == "rag":
            return RagAssistant(
                openai_key=os.getenv("OPENAI_API_KEY"),
                cohere_key=os.getenv("COHERE_API_KEY"),
                knowledge_base=knowledge_base,
                assistant=assistant,
                message_gateway=message_gateway,
                vector_store=vector_store
            )
        elif assistant_type == "no_rag":
            return NoRagAssistant(
                assistant=assistant,
                message_gateway=message_gateway
            )
        elif assistant_type == "sql":
            return TextToSQL(
                assistant=assistant,
                message_gateway=message_gateway,
            )
        elif assistant_type == "agent":
            return AgentGateway(
                message_gateway=message_gateway,
                agent_messages_gateway=agent_message_gateway,
                session_gateway=session_gateway,
                current_user = current_user
            )
        elif assistant_type == "deep_research":
            return DeepResearchGateway(
                message_gateway=message_gateway,
                session_gateway=session_gateway,
                current_user=current_user,
                assistant=assistant,
            )
        else:
            raise ValueError(f"Unknown assistant type: {assistant_type}")