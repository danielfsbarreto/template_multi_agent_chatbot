from pathlib import Path
from typing import Any

from crewai import LLM, Agent

from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.tools import SendMessageToUserTool
from template_multi_agent_chatbot.types import ClassificationResult, Message

_SKILLS_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "user-communication"
)


class MessageClassifierAgent:
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
            role="Message Classifier",
            goal="""Classify the user's message intent. If the request needs to be routed to specialized agents (like image creation or internet search), use the Send Message to User tool to briefly acknowledge the request and let the user know it is being routed to the right experts.
Keep these routing messages natural, varied, and highly contextual to the user's specific request to avoid sounding robotic or repetitive in long chats. Carefully assess the conversation history to ensure you never repeat greetings, phrases, or acknowledgements you have already used. If the request is simple, answer the user directly via the Send Message to User tool.""",
            backstory="""You are a conversational triage agent. You read the conversation history, determine the user's intent, and ensure the user feels heard. When you need to route a request, you send a quick, human-like acknowledgement before doing so. You pride yourself on conversational variety and never using the same canned response twice.
CRITICAL: You must respond solely in the same language the user is using.""",
            llm=LLM(model="anthropic/claude-haiku-4-5"),
            skills=[_SKILLS_PATH],
            tools=[
                SendMessageToUserTool(
                    event_bus=self._event_bus,
                    source=self._source,
                ),
            ],
        )

    def execute(self) -> ClassificationResult:
        messages = [
            {"role": msg.role, "content": msg.content} for msg in self._messages[-10:]
        ]

        result = self._agent().kickoff(
            messages=messages,
            response_format=ClassificationResult,
        )

        return result.pydantic
