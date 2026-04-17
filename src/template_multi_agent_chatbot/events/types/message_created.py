from crewai.events.base_events import BaseEvent
from pydantic import JsonValue


class MessageCreated(BaseEvent):
    type: str = "message_created"

    result: JsonValue
