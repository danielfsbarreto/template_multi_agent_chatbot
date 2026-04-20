from datetime import datetime, timezone

from crewai import LLM, Agent

from template_multi_agent_chatbot.tools import NanoBananaImageGenerationTool
from template_multi_agent_chatbot.types import Message


class ConversationalAgent:
    @classmethod
    def process_request(cls, messages: list[Message]):
        return Message.create(content=cls._agent().kickoff(cls._prompt(messages)).raw)

    @classmethod
    def _agent(cls):
        return Agent(
            role="Conversational Assistant",
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
            # llm=LLM(model="gemini/gemini-3-flash-preview", stream=True),
            tools=[NanoBananaImageGenerationTool()],
        )

    @classmethod
    def _prompt(cls, messages: list[Message]):
        newline = "\n"
        prompt = f"""
        CURRENT DATE AND TIME (UTC):
        {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")}

        CONVERSATION HISTORY (last 10 messages):
        {newline.join([f"[{msg.role.upper()}] {msg.content.strip()}" for msg in messages[-10:]])}

        YOUR TASK:
        Read the conversation history above and respond to the most recent user message.

        KEY RULES:
        - Stay grounded in the conversation history; do not invent prior context
        - Be concise and clear; avoid unnecessary filler
        - Ask a focused clarification question only if the request is genuinely ambiguous
        - Respond in the same language the user is using
        """

        return prompt
