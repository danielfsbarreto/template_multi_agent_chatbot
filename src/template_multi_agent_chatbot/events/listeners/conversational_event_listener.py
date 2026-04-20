from crewai.events import BaseEventListener
from crewai.events.types.llm_events import LLMStreamChunkEvent, LLMThinkingChunkEvent

from template_multi_agent_chatbot.events.clients import Dispatcher
from template_multi_agent_chatbot.events.types import ImageGenerated, MessageCreated


class ConversationalEventListener(BaseEventListener):
    def __init__(self, id: str):
        super().__init__()

        self._dispatcher = Dispatcher()
        self._id = id

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(MessageCreated)
        @crewai_event_bus.on(ImageGenerated)
        @crewai_event_bus.on(LLMStreamChunkEvent)
        @crewai_event_bus.on(LLMThinkingChunkEvent)
        def on_message_created(source, event):
            event.source_fingerprint = self._id
            event.fingerprint_metadata = {"id": self._id}
            self._dispatcher.dispatch(event.to_json())
