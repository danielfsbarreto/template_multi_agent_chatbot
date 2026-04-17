from crewai.events import BaseEventListener, LLMStreamChunkEvent

from template_multi_agent_chatbot.events.clients import Dispatcher
from template_multi_agent_chatbot.events.types import MessageCreated


class ConversationalEventListener(BaseEventListener):
    def __init__(self):
        super().__init__()

        self._dispatcher = Dispatcher()

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(MessageCreated)
        @crewai_event_bus.on(LLMStreamChunkEvent)
        def on_message_created(source, event):
            self._dispatcher.dispatch(event.to_json())
