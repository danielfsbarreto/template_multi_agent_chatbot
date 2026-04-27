from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crewai import LLM, Agent, Crew, Process, Task

from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.tools import (
    NanoBananaImageEditingTool,
    NanoBananaImageGenerationTool,
)
from template_multi_agent_chatbot.types import Message

_IMAGE_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "image-generation"
)
_NEWLINE = "\n"


class ImageCreationCrew:
    def __init__(
        self,
        messages: list[Message],
        event_bus: ConversationalEventBus,
        source: Any,
    ):
        self._messages = messages
        self._event_bus = event_bus
        self._source = source

    def _agent(self) -> Agent:
        return Agent(
            role="CrewAI Image Creation Assistant",
            goal="""Help users create and edit images based on their requests. Your text output is
streamed live to the user in real time — write as if speaking directly to them.

You specialize in understanding what the user wants visually and translating that into
precise prompts for image generation and editing tools. Before calling a tool, briefly
state what you are about to do.

ABSOLUTE RULE: NEVER include file paths, filenames, /tmp/ paths, or storage locations
in any message. The image is delivered automatically — just describe it.""",
            backstory="""You are a creative assistant with deep expertise in image generation and editing.

You excel at interpreting visual requests from conversation context, crafting effective
prompts for image generation models, and iterating on edits when the user wants changes.
CRITICAL: You must respond solely in the same language the user is using.
CRITICAL: You must NEVER reveal file paths, filenames, or storage details.
Images are delivered automatically. Never say "here it is: /tmp/..." or similar.""",
            llm=LLM(model="gemini/gemini-3.1-pro-preview", stream=True),
            skills=[_IMAGE_SKILL_PATH],
            tools=[
                NanoBananaImageGenerationTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
                NanoBananaImageEditingTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
            ],
        )

    def _task(self) -> Task:
        return Task(
            description=f"""Handle the user's image creation or editing request based on the conversation history.
Generate or edit images as requested, and communicate clearly with the user throughout.

IMPORTANT: You must carefully read the conversation history to ensure you are not repeating
information, greetings, or phrases you have already used.

CONVERSATION HISTORY (last 10 messages):
{_NEWLINE.join([f"[{msg.role.upper()}] {msg.content.strip()}" for msg in self._messages[-10:]])}

CURRENT DATE AND TIME (UTC):
{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}
""",
            expected_output="""A helpful response to the user's image request. KEY RULES:
- Stay grounded in the conversation history; do not invent prior context
- Respond in the same language the user is using
- Before calling a tool, briefly state what you are about to do
- NEVER repeat the same content, phrasing, or greetings used in previous messages
- NEVER include file paths, filenames, /tmp/ paths, .png filenames, or storage locations.
  The image is delivered automatically. Just describe what you created.""",
            agent=self._agent(),
        )

    def _crew(self) -> Crew:
        return Crew(
            agents=[self._agent()],
            tasks=[self._task()],
            process=Process.sequential,
            verbose=True,
        )

    def execute(self) -> str:
        return self._crew().kickoff().raw
