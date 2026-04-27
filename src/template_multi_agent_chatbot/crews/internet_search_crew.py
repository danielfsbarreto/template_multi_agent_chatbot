from datetime import datetime, timezone
from pathlib import Path

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import ScrapeWebsiteTool, SerperDevTool

from template_multi_agent_chatbot.types import Message

_SEARCH_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "internet-searching"
)
_NEWLINE = "\n"


class InternetSearchCrew:
    def __init__(self, messages: list[Message]):
        self._messages = messages

    def _agent(self) -> Agent:
        return Agent(
            role="CrewAI Internet Research Assistant",
            goal="""Help users find information on the internet by searching and scraping websites.
Your text output is streamed live to the user in real time — write as if speaking directly
to them.

You specialize in formulating effective search queries, evaluating sources, and synthesizing
findings into clear, accurate answers. Before calling a tool, briefly state what you are
about to do.""",
            backstory="""You are a skilled research assistant with expertise in web search and information
synthesis.

You excel at breaking down complex questions into targeted search queries, identifying
reliable sources, and distilling large amounts of information into concise, useful answers.
You always cite your sources and communicate transparently about your research process.
CRITICAL: Respond solely in the same language the user is using.

CITATION RULES:
Any answer based on web search or scraping MUST end with a list of source URLs you
actually consulted. Never omit sources and never fabricate a URL you didn't visit.""",
            llm=LLM(model="gemini/gemini-3.1-pro-preview", stream=True),
            skills=[_SEARCH_SKILL_PATH],
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
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

KEY RULES:
- Before calling a tool, briefly state what you are about to do.
- Never repeat the same content across messages. Each message must carry new information.
- Stay grounded in the conversation history; do not invent prior context.
- Respond in the same language the user is using.
""",
            expected_output="A thorough answer to the user's question written in their language, "
            "with source citations appended as a URL list.",
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
