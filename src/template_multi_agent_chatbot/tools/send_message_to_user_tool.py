from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, ConfigDict, Field

from template_multi_agent_chatbot.events.conversational_event_bus import (
    ConversationalEventBus,
)
from template_multi_agent_chatbot.types import Message


class SendMessageToUserToolInput(BaseModel):
    content: str = Field(
        ...,
        description=(
            "The message content to send to the user. Write it exactly as the user "
            "should read it, in the user's language, concise and friendly."
        ),
    )


class SendMessageToUserTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Send Message to User"
    description: str = (
        "Send a message to the user. This is the ONLY way the user is notified of "
        "anything you say or do. Call it whenever you want the user to see a message "
        "(acknowledgements, progress updates, clarifying questions, intermediate "
        "findings, or the final answer). Do not call it twice with the same content."
    )
    args_schema: Type[BaseModel] = SendMessageToUserToolInput

    event_bus: ConversationalEventBus
    source: Any

    def _run(self, content: str) -> str:
        message = Message.create(content=content)
        self.event_bus.emit_message_created(self.source, message)

        return "Message delivered to the user."
