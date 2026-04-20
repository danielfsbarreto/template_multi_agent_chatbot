from crewai.events.base_events import BaseEvent
from pydantic import JsonValue


class ImageGenerated(BaseEvent):
    type: str = "image_generated"

    result: JsonValue
