from typing import ClassVar, Type
from uuid import uuid4

from crewai.tools import BaseTool
from google import genai
from pydantic import BaseModel, Field


class NanoBananaImageGenerationToolInput(BaseModel):
    prompt: str = Field(..., description="The prompt to generate the image.")


class NanoBananaImageGenerationTool(BaseTool):
    name: str = "Nano Banana Image Generation"
    description: str = "Generate an image through Nano Banana based on a user prompt."
    args_schema: Type[BaseModel] = NanoBananaImageGenerationToolInput

    client: ClassVar[genai.Client] = genai.Client()

    def _run(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[prompt],
        )
        uuid_filename = str(uuid4())

        for part in response.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = part.as_image()
                image.save(f"out/generated_image_{uuid_filename}.png")

                return "Image generated successfully."

            return "Failed to generate image."

        return "Failed to generate image."
