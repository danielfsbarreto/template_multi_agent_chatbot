#!/usr/bin/env python

from typing import Literal

from crewai.flow import Flow, listen, or_, persist, router, start

from template_multi_agent_chatbot.agents import MessageClassifierAgent
from template_multi_agent_chatbot.crews import (
    CrewaiDocsCrew,
    ImageCreationCrew,
    InternetSearchCrew,
)
from template_multi_agent_chatbot.events import ConversationalEventBus
from template_multi_agent_chatbot.types import ConversationalState, Message


@persist()
class ConversationalFlow(Flow[ConversationalState]):
    @start()
    def load_initial_context(self):
        self.event_bus = ConversationalEventBus(self)
        self.state.messages.append(self.state.user_message)

    @router(load_initial_context)
    def classify_message(
        self,
    ) -> Literal["SIMPLE", "IMAGE_CREATION_UPDATE", "INTERNET_SEARCH", "CREWAI_DOCS"]:
        classification, response = MessageClassifierAgent(
            messages=self.state.messages,
        ).execute()

        self.state.messages.append(Message(role="assistant", content=response))

        return classification

    @listen("SIMPLE")
    def handle_simple_message(self):
        pass

    @listen("IMAGE_CREATION_UPDATE")
    def handle_image_creation(self):
        message = Message(
            role="assistant",
            content=ImageCreationCrew(
                messages=self.state.messages,
                event_bus=self.event_bus,
                source=self.handle_image_creation,
            ).execute(),
        )
        self.state.messages.append(message)
        return message

    @listen("INTERNET_SEARCH")
    def handle_internet_search(self):
        message = Message(
            role="assistant",
            content=InternetSearchCrew(
                messages=self.state.messages,
            ).execute(),
        )
        self.state.messages.append(message)
        return message

    @listen("CREWAI_DOCS")
    def handle_crewai_docs(self):
        message = Message(
            role="assistant",
            content=CrewaiDocsCrew(
                messages=self.state.messages,
            ).execute(),
        )
        self.state.messages.append(message)
        return message

    @listen(
        or_(
            handle_simple_message,
            handle_image_creation,
            handle_internet_search,
            handle_crewai_docs,
        )
    )
    def finalize(self):
        return self.state.model_dump()


def kickoff():
    ConversationalFlow().kickoff(
        inputs={
            "user_message": {
                "role": "user",
                # "content": "Hello, how are you?",  # SIMPLE ROUTE
                # "content": "Generate an image of an otter playing with a ball", # IMAGE ROUTE
                # "content": "Do a quick search about retro emulation", # SEARCH ROUTE
                "content": "How do I create a crew with custom tools in CrewAI?",  # CREWAI DOCS ROUTE
            },
        }
    )


def plot():
    ConversationalFlow().plot()


if __name__ == "__main__":
    kickoff()
