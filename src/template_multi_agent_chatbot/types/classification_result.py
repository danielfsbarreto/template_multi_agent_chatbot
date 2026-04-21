from typing import Literal

from pydantic import BaseModel


class ClassificationResult(BaseModel):
    classification: Literal["SIMPLE", "IMAGE_CREATION_UPDATE", "INTERNET_SEARCH"]
