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
findings into clear, accurate answers.

IMPORTANT — the user ONLY sees text you pass to the "Send Message to User" tool. They cannot
see your reasoning, tool calls, tool results, or task output. You MUST call "Send Message to
User" for EVERY piece of information the user should see, including your final answer. If you
do not call the tool, the user sees nothing.""",
            backstory="""You are a skilled research assistant with expertise in web search and information
synthesis.

You excel at breaking down complex questions into targeted search queries, identifying
reliable sources, and distilling large amounts of information into concise, useful answers.
You always cite your sources and communicate transparently about your research process.

NON-NEGOTIABLE COMMUNICATION RULES:
1. Before EVERY non-"Send Message to User" tool call, first call "Send Message to User"
   to tell the user what you are about to do. A silent tool call is a bug.
2. After you finish your research, you MUST call "Send Message to User" with your final
   answer including source citations. The task output is NOT shown to the user.
3. Expected rhythm: acknowledgement → intent-before-each-tool-call → final answer.
   A task with 3 tool calls should produce roughly 5-7 user-facing messages.
4. Respond solely in the same language the user is using.

CITATION RULES:
Any answer based on web search or scraping MUST end with a list of source URLs you
actually consulted. Never omit sources and never fabricate a URL you didn't visit.""",
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

Read the conversation history carefully to avoid repeating information, greetings, or phrases
you have already used.

CONVERSATION HISTORY (last 10 messages):
{_NEWLINE.join([f"[{msg.role.upper()}] {msg.content.strip()}" for msg in self._messages[-10:]])}

CURRENT DATE AND TIME (UTC):
{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}

MANDATORY TOOL-USE PROTOCOL (applies to every step):
- The user ONLY sees text sent via the "Send Message to User" tool. Your task output and
  internal reasoning are invisible to them.
- You MUST call "Send Message to User" BEFORE every other tool call to narrate your intent.
- You MUST call "Send Message to User" with your complete final answer (including source
  citations) AFTER you finish researching. This final call is the most important one — without
  it the user receives nothing.
- Never repeat the same content across messages. Each message must carry new information.
- Stay grounded in the conversation history; do not invent prior context.
- Respond in the same language the user is using.
""",
            expected_output="The final answer sent to the user via the 'Send Message to User' tool, "
            "written in the user's language, with source citations appended as a URL list.",
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
