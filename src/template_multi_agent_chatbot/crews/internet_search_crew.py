from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.tools import SendMessageToUserTool
from template_multi_agent_chatbot.types import Message

_USER_COMM_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "user-communication"
)
_SEARCH_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "internet-searching"
)
_NEWLINE = "\n"


class InternetSearchCrew:
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
            role="CrewAI Internet Research Assistant",
            goal="""Help users find information on the internet by searching and scraping websites.

You specialize in formulating effective search queries, evaluating sources, and synthesizing
findings into clear, accurate answers. You always keep the user informed about your research
progress.""",
            backstory="""You are a skilled research assistant with expertise in web search and information
synthesis.

You excel at breaking down complex questions into targeted search queries, identifying
reliable sources, and distilling large amounts of information into concise, useful answers.
You always cite your sources and communicate transparently about your research process.
CRITICAL: You must respond solely in the same language the user is using.""",
            llm=LLM(model="gemini/gemini-3.1-pro-preview", stream=True),
            skills=[_USER_COMM_SKILL_PATH, _SEARCH_SKILL_PATH],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                SendMessageToUserTool(
                    event_bus=self._event_bus,
                ),
            ],
        )

    def _task(self) -> Task:
        return Task(
            description=f"""Research the user's question using internet search and web scraping as needed.
Provide a thorough, well-sourced answer based on the conversation history.

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
- Cite sources when presenting research findings""",
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
