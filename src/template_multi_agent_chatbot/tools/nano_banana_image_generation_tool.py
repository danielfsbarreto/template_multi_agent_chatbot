import base64
from datetime import datetime, timezone
from typing import Any, ClassVar, Type

from crewai.tools import BaseTool
from google import genai
from pydantic import BaseModel, ConfigDict, Field

from template_multi_agent_chatbot.events.conversational_event_bus import (
    ConversationalEventBus,
)


class NanoBananaImageGenerationToolInput(BaseModel):
    prompt: str = Field(..., description="The prompt to generate the image.")


class NanoBananaImageGenerationTool(BaseTool):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str = "Nano Banana Image Generation"
    description: str = "Generate an image through Nano Banana based on a user prompt."
    args_schema: Type[BaseModel] = NanoBananaImageGenerationToolInput

    event_bus: ConversationalEventBus
    source: Any

    client: ClassVar[genai.Client] = genai.Client()

    def _run(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt],
        )
        filename = datetime.now(timezone.utc).strftime("%H%M%S")

        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = part.as_image()
                image.save(f"out/{filename}.png")

                image_bytes = open(f"out/{filename}.png", "rb").read()
                image_base64 = base64.b64encode(image_bytes).decode("utf-8")
                self.event_bus.emit_image_generated(self.source, image_base64)

                return "Image generated successfully."

            return "Failed to generate image."

        return "Failed to generate image."
