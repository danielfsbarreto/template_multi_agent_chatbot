from typing import Callable

from crewai.events.event_bus import crewai_event_bus

from template_multi_agent_chatbot.events.listeners import ConversationalEventListener
from template_multi_agent_chatbot.events.types import ImageGenerated, MessageCreated
from template_multi_agent_chatbot.types import Message


class ConversationalEventBus:
    def __init__(self, flow: object):
        self._flow = flow

    def register_listener(self):
        ConversationalEventListener(id=self._flow.state.id)

    def emit_message_created(self, source: Callable, message: Message):
        self._flow.state.messages.append(message)

        crewai_event_bus.emit(
            source=source,
            event=MessageCreated(
                source_type=source.__name__,
                result={"message": message.model_dump()},
            ),
        )

    def emit_image_generated(self, source: Callable, image_base64: str):
        crewai_event_bus.emit(
            source=source,
            event=ImageGenerated(
                source_type=source.__name__,
                result={"image": image_base64},
            ),
        )
