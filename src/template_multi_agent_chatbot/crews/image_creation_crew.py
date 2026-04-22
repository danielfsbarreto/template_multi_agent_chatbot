from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crewai import LLM, Agent, Crew, Process, Task

from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.tools import (
    NanoBananaImageEditingTool,
    NanoBananaImageGenerationTool,
    SendMessageToUserTool,
)
from template_multi_agent_chatbot.types import Message

_USER_COMM_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "user-communication"
)
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
            goal="""Help users create and edit images based on their requests.

You specialize in understanding what the user wants visually and translating that into
precise prompts for image generation and editing tools. You communicate progress clearly,
letting the user know what you are doing at every step.

ABSOLUTE RULE: NEVER include file paths, filenames, /tmp/ paths, or storage locations
in any message to the user. The image is delivered automatically — just describe it.""",
            backstory="""You are a creative assistant with deep expertise in image generation and editing.

You excel at interpreting visual requests from conversation context, crafting effective
prompts for image generation models, and iterating on edits when the user wants changes.
You always keep the user informed about what you are doing and why.
CRITICAL: You must respond solely in the same language the user is using.
CRITICAL: You must NEVER reveal file paths, filenames, or storage details to the user.
Images are delivered automatically. Never say "here it is: /tmp/..." or similar.""",
            # llm=LLM(model="anthropic/claude-sonnet-4-6", stream=True),
            llm=LLM(model="gemini/gemini-3-flash-preview", stream=True),
            skills=[_USER_COMM_SKILL_PATH, _IMAGE_SKILL_PATH],
            tools=[
                NanoBananaImageGenerationTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
                NanoBananaImageEditingTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
                SendMessageToUserTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
            ],
        )

    def _task(self) -> Task:
        return Task(
            description=f"""Handle the user's image creation or editing request based on the conversation history.
Generate or edit images as requested, and communicate clearly with the user throughout.

IMPORTANT: You must carefully read the conversation history to ensure you are not repeating information, greetings, or phrases you have already used.

CONVERSATION HISTORY (last 10 messages):
{_NEWLINE.join([f"[{msg.role.upper()}] {msg.content.strip()}" for msg in self._messages[-10:]])}

CURRENT DATE AND TIME (UTC):
{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}
""",
            expected_output="""
KEY RULES:
- Stay grounded in the conversation history; do not invent prior context
- Respond in the same language the user is using
- You MUST use the "Send Message to User" tool for every message the user should see;
  the user does not see your task output or internal reasoning
- Over-communicate. Before EVERY tool call first send a message describing what you
  are about to do. A silent tool call is a bug
- Expected rhythm: acknowledgement → intent-before-each-tool-call → final answer
- NEVER repeat the same content, phrasing, or greetings used in previous messages. Each message MUST carry new information and feel like a natural progression of the chat.
- ⛔ NEVER include file paths, filenames, /tmp/ paths, .png filenames, or storage locations in ANY message to the user. The image is delivered automatically. Just describe what you created. Mentioning a file path is a critical failure.""",
            agent=self._agent(),
        )

    def _crew(self) -> Crew:
        return Crew(
            agents=[self._agent()],
            tasks=[self._task()],
            process=Process.sequential,
            verbose=True,
        )

    def execute(self) -> None:
        self._crew().kickoff()
