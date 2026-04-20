#!/usr/bin/env python

from crewai.flow import Flow, and_, listen, persist, start

from template_multi_agent_chatbot.crews import HandleUserMessageCrew
from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.types import ConversationalState


@persist()
class ConversationalFlow(Flow[ConversationalState]):
    @start()
    def load_initial_context(self):
        self.state.messages.append(self.state.user_message)

    @start()
    def load_event_bus(self):
        self.event_bus = ConversationalEventBus(self)

    @listen(and_(load_initial_context, load_event_bus))
    def handle_new_message(self):
        # message = ConversationalAgent.process_request(self.state.messages)
        message = HandleUserMessageCrew(self.state.messages).execute()

        self.event_bus.emit_message_created(self.handle_new_message, message)


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "user_message": {
                "role": "user",
                "content": "Oi, tudo bem?",
            },
        }
    )


def plot():
    ConversationalFlow().plot()


if __name__ == "__main__":
    kickoff()
