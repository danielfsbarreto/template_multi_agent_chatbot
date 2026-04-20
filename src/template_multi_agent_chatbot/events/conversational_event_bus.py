from typing import Callable

from crewai.events.event_bus import crewai_event_bus

from template_multi_agent_chatbot.events.listeners import ConversationalEventListener
from template_multi_agent_chatbot.events.types import MessageCreated
from template_multi_agent_chatbot.types import Message


class ConversationalEventBus:
    def __init__(self, flow: object):
        self._id = flow.state.id

        ConversationalEventListener(id=self._id)

    def emit_message_created(self, source: Callable, message: Message):
        crewai_event_bus.emit(
            source=source,
            event=MessageCreated(
                source_type=source.__name__,
                result={"message": message.model_dump()},
            ),
        )
