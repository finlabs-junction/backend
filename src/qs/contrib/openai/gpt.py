from __future__ import annotations

import typing as t

import msgspec
from msgspec import Struct
from qs.nlp import LLM, Preset, Role, Thread

from openai import AsyncOpenAI, LengthFinishReasonError
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)

__all__ = [
    "GPTSettings",
    "GPT",
]


T = t.TypeVar("T")


class GPTSettings(Struct):
    model: str
    max_tokens: int
    temperature: dict[Preset, float]
    top_p: dict[Preset, float]
    frequency_penalty: float
    presence_penalty: float


def disallow_extra_properties(schema):
    if schema.get("type") == "object":
        schema["additionalProperties"] = False

        for value in schema["properties"].values():
            disallow_extra_properties(value)


class GPT(LLM):
    def __init__(
        self,
        client: AsyncOpenAI,
        settings: GPTSettings,
    ):
        self._client = client
        self.settings = settings


    @t.override
    async def generate_text_response(
        self,
        thread: Thread,
        preset: Preset,
    ) -> str:
        completion = await self._client.chat.completions.create(
            model=self.settings.model,
            messages=format_thread_like_openai(thread),
            temperature=self.settings.temperature[preset],
            max_tokens=self.settings.max_tokens,
            top_p=self.settings.top_p[preset],
            frequency_penalty=self.settings.frequency_penalty,
            presence_penalty=self.settings.presence_penalty,
        )

        response = completion.choices[0]

        if response.finish_reason != "stop":
            raise ValueError(f"Completion finished with reason '{response.finish_reason}'.")

        if response.message.content is None:
            raise ValueError("Completion message content is None.")

        return response.message.content


    @t.override
    async def generate_json_response(
        self,
        thread: Thread,
        preset: Preset,
    ) -> dict[str, t.Any]:
        completion = await self._client.chat.completions.create(
            model=self.settings.model,
            messages=format_thread_like_openai(thread),
            response_format={"type": "json_object"},
            temperature=self.settings.temperature[preset],
            max_tokens=self.settings.max_tokens,
            top_p=self.settings.top_p[preset],
            frequency_penalty=self.settings.frequency_penalty,
            presence_penalty=self.settings.presence_penalty,
        )

        response = completion.choices[0]

        if response.finish_reason != "stop":
            raise ValueError(
                f"Completion finished with reason '{response.finish_reason}'.",
            )

        if response.message.content is None:
            raise ValueError("Completion message content is None.")

        return msgspec.json.decode(response.message.content)


    @t.override
    async def generate_structured_response(
        self,
        thread: Thread,
        model: type[T],
        preset: Preset,
    ) -> T:
        try:
            schema = msgspec.json.schema(model)

            for definition in schema["$defs"].values():
                disallow_extra_properties(definition)

            schema = {
                "type": "object",
                "properties": schema["$defs"][model.__name__]["properties"],
                "additionalProperties": False,
                "required": schema["$defs"][model.__name__]["required"],
                "$defs": schema["$defs"],
            }

            del schema["$defs"][model.__name__]

            completion = await self._client.chat.completions.create(
                model=self.settings.model,
                messages=format_thread_like_openai(thread),
                temperature=self.settings.temperature[preset],
                max_tokens=self.settings.max_tokens,
                top_p=self.settings.top_p[preset],
                frequency_penalty=self.settings.frequency_penalty,
                presence_penalty=self.settings.presence_penalty,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": model.__name__,
                        "strict": True,
                        "schema": schema,
                    },
                },
            )

            response = completion.choices[0].message.content

            if response is None:
                raise ValueError("Completion message content is None.")

            return msgspec.json.decode(response, type=model)

        except LengthFinishReasonError as e:
            raise ValueError(f"Completion stopped due to reaching max tokens: '{e}'.")

        except Exception as e:
            raise e


    @classmethod
    def flagship(
        cls,
        api_key: str | None = None,
        client: AsyncOpenAI | None = None,
    ) -> GPT:
        return cls.create(model="gpt-4o", api_key=api_key, client=client)


    @classmethod
    def small(
        cls,
        api_key: str | None = None,
        client: AsyncOpenAI | None = None,
    ) -> GPT:
        return cls.create(model="gpt-4o-mini", api_key=api_key, client=client)
    

    @classmethod
    def create(
        cls,
        model: str,
        api_key: str | None = None,
        client: AsyncOpenAI | None = None,
    ) -> GPT:
        if client is None:
            if api_key is None:
                raise ValueError("Provide either an API key or a client.")

            client = AsyncOpenAI(api_key=api_key)

        return cls(
            client=client,
            settings=GPTSettings(
                model=model,
                temperature={
                    Preset.Predictable: 0.5,
                    Preset.Neutral: 0.7,
                    Preset.Creative: 1.0,
                },
                max_tokens=1024,
                top_p={
                    Preset.Predictable: 0.5,
                    Preset.Neutral: 0.9,
                    Preset.Creative: 1.0,
                },
                frequency_penalty=0.0,
                presence_penalty=0.0,
            ),
        )


def format_thread_like_openai(
    thread: Thread,
) -> list[ChatCompletionMessageParam]:
    result: list[ChatCompletionMessageParam] = []

    system_message = ChatCompletionSystemMessageParam(
        role="system",
        content=thread.instruction,
    )

    result.append(system_message)

    for message in thread.messages:
        if message.role == Role.User:
            openai_message = ChatCompletionUserMessageParam(
                role="user",
                content=message.content,
            )
        elif message.role == Role.Assistant:
            openai_message = ChatCompletionAssistantMessageParam(
                role="assistant",
                content=message.content,
            )
        elif message.role == Role.System:
            openai_message = ChatCompletionSystemMessageParam(
                role="system",
                content=message.content,
            )
        else:
            raise NotImplementedError(f"Role {message.role} is not supported.")

        openai_message = result.append(openai_message)

    return result
