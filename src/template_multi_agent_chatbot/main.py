#!/usr/bin/env python

from crewai.flow import Flow, listen, or_, persist, router, start

from template_multi_agent_chatbot.agents import MessageClassifierAgent
from template_multi_agent_chatbot.crews import ImageCreationCrew, InternetSearchCrew
from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.types import ConversationalState


@persist()
class ConversationalFlow(Flow[ConversationalState]):
    @start()
    def load_initial_context(self):
        self.event_bus = ConversationalEventBus(self)
        self.state.messages.append(self.state.user_message)

    @router(load_initial_context)
    def classify_message(self):
        result = MessageClassifierAgent(
            messages=self.state.messages,
            event_bus=self.event_bus,
            source=self.classify_message,
        ).execute()

        return result.classification

    @listen("SIMPLE")
    def handle_simple_message(self):
        pass

    @listen("IMAGE_CREATION_UPDATE")
    def handle_image_creation(self):
        ImageCreationCrew(
            messages=self.state.messages,
            event_bus=self.event_bus,
            source=self.handle_image_creation,
        ).execute()

    @listen("INTERNET_SEARCH")
    def handle_internet_search(self):
        InternetSearchCrew(
            messages=self.state.messages,
            event_bus=self.event_bus,
            source=self.handle_internet_search,
        ).execute()

    @listen(or_(handle_simple_message, handle_image_creation, handle_internet_search))
    def finalize(self):
        return self.state.model_dump()


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "user_message": {
                "role": "user",
                "content": "search about latest news regarding openai",
            },
        }
    )


def plot():
    ConversationalFlow().plot()


if __name__ == "__main__":
    kickoff()
