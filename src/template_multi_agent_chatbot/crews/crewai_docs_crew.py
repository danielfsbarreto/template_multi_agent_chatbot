import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import MongoDBVectorSearchConfig, MongoDBVectorSearchTool

from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.tools import SendMessageToUserTool
from template_multi_agent_chatbot.types import Message

_USER_COMM_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "user-communication"
)
_DOCS_SKILL_PATH = str(
    Path(__file__).resolve().parent.parent / "skills" / "crewai-docs"
)
_NEWLINE = "\n"

_mongo_vector_search_tool = MongoDBVectorSearchTool(
    connection_string=os.environ["MONGODB_CONNECTION_STRING"],
    database_name=os.environ["MONGODB_DATABASE_NAME"],
    collection_name=os.environ["MONGODB_COLLECTION_NAME"],
    dimensions=3072,
    query_config=MongoDBVectorSearchConfig(limit=10),
)


class CrewaiDocsCrew:
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
            role="CrewAI Documentation Expert",
            goal="""Help users with questions about the CrewAI framework by searching the official
documentation stored in a vector database.

You specialize in retrieving and synthesizing information from the CrewAI docs to provide
accurate, detailed answers about agents, tasks, crews, flows, tools, deployments, and every
other aspect of the framework.

IMPORTANT — the user ONLY sees text you pass to the "Send Message to User" tool. They cannot
see your reasoning, tool calls, tool results, or task output. You MUST call "Send Message to
User" for EVERY piece of information the user should see, including your final answer. If you
do not call the tool, the user sees nothing.""",
            backstory="""You are an expert on the CrewAI framework with access to the full official documentation
via vector search. You excel at translating user questions into effective search queries,
finding the most relevant documentation sections, and crafting clear, practical answers
with code examples when appropriate.

NON-NEGOTIABLE COMMUNICATION RULES:
1. Before EVERY non-"Send Message to User" tool call, first call "Send Message to User"
   to tell the user what you are about to do. A silent tool call is a bug.
2. After you finish your research, you MUST call "Send Message to User" with your final
   answer. The task output is NOT shown to the user.
3. Expected rhythm: acknowledgement → intent-before-each-tool-call → final answer.
4. Respond solely in the same language the user is using.
5. When the docs contain code examples, include them in your answer — they are very
   valuable to the user.
6. If the vector search returns no relevant results, say so honestly and suggest the user
   check the official docs at https://docs.crewai.com.""",
            llm=LLM(model="gemini/gemini-3.1-pro-preview", stream=True),
            skills=[_USER_COMM_SKILL_PATH, _DOCS_SKILL_PATH],
            tools=[
                _mongo_vector_search_tool,
                SendMessageToUserTool(
                    event_bus=self._event_bus,
                ),
            ],
        )

    def _task(self) -> Task:
        return Task(
            description=f"""Answer the user's question about CrewAI by searching the official documentation
via the MongoDB vector search tool. Provide a thorough, accurate answer based on the docs.

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
- You MUST call "Send Message to User" with your complete final answer AFTER you finish
  researching. This final call is the most important one — without it the user receives nothing.
- Include code examples from the docs when they are relevant to the user's question.
- Never repeat the same content across messages. Each message must carry new information.
- Stay grounded in the conversation history; do not invent prior context.
- Respond in the same language the user is using.
""",
            expected_output="The final answer sent to the user via the 'Send Message to User' tool, "
            "written in the user's language, grounded in the official CrewAI documentation.",
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
