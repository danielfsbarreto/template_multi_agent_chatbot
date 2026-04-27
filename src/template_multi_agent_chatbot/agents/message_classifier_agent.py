from crewai import LLM, Agent

from template_multi_agent_chatbot.types import ClassificationResult, Message

_LLM = LLM(model="gemini/gemini-3-flash-preview", stream=True)

_ROUTE_DESCRIPTIONS = {
    "IMAGE_CREATION_UPDATE": "image creation",
    "INTERNET_SEARCH": "web search",
    "CREWAI_DOCS": "CrewAI documentation lookup",
}


class MessageClassifierAgent:
    def __init__(self, messages: list[Message]):
        self._messages = messages

    def execute(self) -> tuple[str, str]:
        messages = [
            {"role": msg.role, "content": msg.content} for msg in self._messages[-10:]
        ]

        classification = self._classify(messages)
        response = self._respond(messages, classification)

        return classification, response

    # -- Step 1: structured output → JSON, filtered from streaming ----------------

    def _classify(self, messages: list[dict]) -> str:
        return (
            Agent(
                role="Message Classifier",
                goal="Classify the user's message intent into exactly one route.",
                backstory="""You are a triage agent that reads conversation history and picks the right route.
CRITICAL: When the user asks anything about CrewAI (the framework), always classify as CREWAI_DOCS — never SIMPLE or INTERNET_SEARCH.

ROUTING GUIDE:
- CREWAI_DOCS: Any question about CrewAI — the framework, its Python API, agents, tasks, crews, flows, tools, pipelines, deployments, configuration, or how to build with CrewAI.
- IMAGE_CREATION_UPDATE: Requests to generate or edit images.
- INTERNET_SEARCH: Questions requiring up-to-date web information, current events, or facts that may have changed.
- SIMPLE: Greetings, small talk, or general questions you can answer directly without specialized tools.""",
                llm=_LLM,
            )
            .kickoff(messages=messages, response_format=ClassificationResult)
            .pydantic.classification
        )

    # -- Step 2: plain text → streamed live to UI ---------------------------------

    def _respond(self, messages: list[dict], classification: str) -> str:
        label = _ROUTE_DESCRIPTIONS.get(classification, "direct conversation")
        instruction = (
            f"The user's request has been classified as: {classification} ({label}). "
            "Write a natural, context-aware response to the user. "
            "If the request was classified as simple (greetings, small talk), answer it directly. "
            "Otherwise, it will be handled by a specialized agent. Therefore, briefly acknowledge "
            "the request and let them know the right agents are being selected to help. "
            "Keep routed acknowledgments short (1-2 sentences). "
            "Vary your phrasing — never repeat the same canned response."
        )

        return (
            Agent(
                role="Message Classifier",
                goal=instruction,
                backstory="""You are a conversational agent. Your text output is streamed live to the user in real time.
Carefully assess the conversation history to avoid repeating greetings, phrases, or acknowledgements.
CRITICAL: You must respond solely in the same language the user is using.""",
                llm=_LLM,
            )
            .kickoff(messages=messages)
            .raw
        )
