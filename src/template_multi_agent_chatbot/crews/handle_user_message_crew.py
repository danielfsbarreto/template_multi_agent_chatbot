from datetime import datetime, timezone

from crewai import LLM, Agent, Crew, Process, Task

from template_multi_agent_chatbot.types import Message


class HandleUserMessageCrew:
    _NEWLINE = "\n"

    def __init__(self, messages: list[Message]):
        self._messages = messages

    def _conversational_agent(self) -> Agent:
        return Agent(
            role="CrewAI Conversational Assistant",
            goal="""Engage users in natural, helpful conversation and provide clear, accurate responses
to their questions.

Your primary function is to understand the user's intent from the conversation history and
respond in a way that is concise, friendly, and genuinely useful. Ask for clarification only
when the request is truly ambiguous.""",
            backstory="""You are a helpful conversational assistant designed to chat with users in a
natural and approachable way.

You excel at maintaining context across a conversation, remembering what has been said, and
tailoring your responses accordingly. You communicate clearly and concisely, avoiding
unnecessary jargon while still being informative.

You are thoughtful and grounded in the conversation history. You prioritize being useful
over being verbose, and you never invent information you are not sure about.""",
            llm=LLM(model="gpt-4.1-mini", stream=True),
        )

    def _task_one(self) -> Task:
        return Task(
            description=f"""Interpret the latest user message in the context of the conversation so far.
Draw on the entire message history to understand what the user truly wants.
Reply with a response that is helpful, informative, and easy to understand.
If you are uncertain about user intent, politely ask for clarification rather than guessing.

CONVERSATION HISTORY (last 10 messages):
{self._NEWLINE.join([f"[{msg.role.upper()}] {msg.content.strip()}" for msg in self._messages[-10:]])}

CURRENT DATE AND TIME (UTC):
{datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}
""",
            expected_output="""
KEY RULES:
- Stay grounded in the conversation history; do not invent prior context
- Be concise and clear; avoid unnecessary filler
- Ask a focused clarification question only if the request is genuinely ambiguous
- Respond in the same language the user is using""",
            agent=self._conversational_agent(),
        )

    def _crew(self) -> Crew:
        return Crew(
            agents=[self._conversational_agent()],
            tasks=[self._task_one()],
            process=Process.sequential,
            verbose=True,
        )

    def execute(self) -> str:
        return Message.create(content=self._crew().kickoff().raw)
