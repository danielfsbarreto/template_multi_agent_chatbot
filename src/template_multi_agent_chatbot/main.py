#!/usr/bin/env python

from crewai.flow import Flow, listen, persist, start

from template_multi_agent_chatbot.crews import HandleUserMessageCrew
from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.types import ConversationalState


@persist()
class ConversationalFlow(Flow[ConversationalState]):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.event_bus = ConversationalEventBus(self)

    @start()
    def load_initial_context(self):
        self.event_bus.register_listener()

        self.state.messages.append(self.state.user_message)

    @listen(load_initial_context)
    def handle_new_message(self):
        HandleUserMessageCrew(
            messages=self.state.messages,
            event_bus=self.event_bus,
            source=self.handle_new_message,
        ).execute()


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
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
