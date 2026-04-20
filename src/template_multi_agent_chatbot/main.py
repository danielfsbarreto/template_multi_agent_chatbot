#!/usr/bin/env python

from crewai.flow import Flow, listen, start

from template_multi_agent_chatbot.crews import HandleUserMessageCrew
from template_multi_agent_chatbot.db import MessageRepository, init_db
from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.types import ConversationalState

init_db()


class ConversationalFlow(Flow[ConversationalState]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.messages: list = []
        self.message_repo = MessageRepository()
        self.event_bus = ConversationalEventBus(self, self.message_repo)

    @start()
    def load_initial_context(self):
        self.event_bus.register_listener()

        cid = self.state.conversation_id
        user_message = self.state.user_message

        self.messages = self.message_repo.find_by_conversation(cid)
        self.messages.append(user_message)
        self.message_repo.add(cid, user_message)

    @listen(load_initial_context)
    def handle_new_message(self):
        HandleUserMessageCrew(
            messages=self.messages,
            event_bus=self.event_bus,
            source=self.handle_new_message,
        ).execute()


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "conversation_id": "test-conversation",
            "user_message": {
                "role": "user",
                "content": "Gera uma imagem de uma banana com o estilo gráfico do Studio Ghibli.",
            },
        }
    )


def plot():
    ConversationalFlow().plot()


if __name__ == "__main__":
    kickoff()
