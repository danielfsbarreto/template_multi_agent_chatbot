from pydantic import BaseModel

from template_multi_agent_chatbot.types.message import Message


class ConversationalState(BaseModel):
    conversation_id: str = ""
    user_message: Message | None = None
