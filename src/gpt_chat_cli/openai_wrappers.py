import json
import openai

from typing import Any, List, Optional, Generator
from dataclasses import dataclass
from enum import Enum, auto

@dataclass
class Delta:
    content: Optional[str] = None
    role: Optional[str] = None

class FinishReason(Enum):
    STOP = auto()
    MAX_TOKENS = auto()
    TEMPERATURE = auto()
    NONE = auto()

    @staticmethod
    def from_str(finish_reason_str : Optional[str]) -> "FinishReason":
        if finish_reason_str is None:
            return FinishReason.NONE
        return FinishReason[finish_reason_str.upper()]

@dataclass
class Choice:
    delta: Delta
    finish_reason: Optional[FinishReason]
    index: int

class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

@dataclass
class ChatMessage:
    role: Role
    content: str

    def to_json(self : "ChatMessage"):
        return {
            "role": self.role.value,
            "content": self.content
        }

ChatHistory = List[ChatMessage]

@dataclass
class OpenAIChatResponse:
    choices: List[Choice]
    created: int
    id: str
    model: str
    object: str

    def from_json(data: Any) -> "OpenAIChatResponse":
        choices = []

        for choice in data["choices"]:
            delta = Delta(
                content=choice["delta"].get("content"),
                role=choice["delta"].get("role")
            )

            choices.append(Choice(
                delta=delta,
                finish_reason=FinishReason.from_str(choice["finish_reason"]),
                index=choice["index"],
            ))

        return OpenAIChatResponse(
            choices,
            created=data["created"],
            id=data["id"],
            model=data["model"],
            object=data["object"],
        )

OpenAIChatResponseStream = Generator[OpenAIChatResponse, None, None]

from .argparsing import CompletionArguments

def create_chat_completion(hist : ChatHistory, args: CompletionArguments) \
    -> OpenAIChatResponseStream:

    messages = [ msg.to_json() for msg in hist ]

    response = openai.ChatCompletion.create(
        model=args.model,
        messages=messages,
        n=args.n_completions,
        temperature=args.temperature,
        presence_penalty=args.presence_penalty,
        frequency_penalty=args.frequency_penalty,
        max_tokens=args.max_tokens,
        top_p=args.top_p,
        stream=True
    )

    return (
        OpenAIChatResponse.from_json( update ) \
        for update in response
    )


def list_models() -> List[str]:

    model_data = openai.Model.list()

    models = []

    for model in model_data["data"]:
        models.append(model["id"])

    models.sort()

    return models
