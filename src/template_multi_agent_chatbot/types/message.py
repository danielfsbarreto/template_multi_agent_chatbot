from typing import Literal

from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

    @classmethod
    def create(cls, content: str, role: Literal["user", "assistant"] = "assistant"):
        return cls(role=role, content=content)
