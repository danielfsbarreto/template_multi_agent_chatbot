from crewai.events import (
    BaseEventListener,
    FlowFinishedEvent,
    ToolUsageErrorEvent,
    ToolUsageFinishedEvent,
    ToolUsageStartedEvent,
)
from crewai.events.types.llm_events import LLMStreamChunkEvent, LLMThinkingChunkEvent

from template_multi_agent_chatbot.events.clients import Dispatcher
from template_multi_agent_chatbot.events.types import ImageGenerated


class ConversationalEventListener(BaseEventListener):
    def __init__(self, id: str):
        super().__init__()

        self._dispatcher = Dispatcher()
        self._id = id

    def setup_listeners(self, crewai_event_bus):
        @crewai_event_bus.on(ImageGenerated)
        @crewai_event_bus.on(LLMStreamChunkEvent)
        @crewai_event_bus.on(LLMThinkingChunkEvent)
        @crewai_event_bus.on(FlowFinishedEvent)
        @crewai_event_bus.on(ToolUsageFinishedEvent)
        @crewai_event_bus.on(ToolUsageStartedEvent)
        @crewai_event_bus.on(ToolUsageErrorEvent)
        def on_event(source, event):
            if not event.source_fingerprint:
                event.source_fingerprint = self._id

            if not event.fingerprint_metadata:
                event.fingerprint_metadata = {"conversation_id": self._id}

            self._dispatcher.dispatch(event.to_json())
