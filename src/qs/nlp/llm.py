from __future__ import annotations

import enum
import functools
import inspect
import typing as t
from abc import ABC, abstractmethod

import msgspec
from msgspec import Struct
from qs.cache import lru_cache

__all__ = [
    "Role",
    "Message",
    "Preset",
    "Thread",
    "LLM",
]


class Role(enum.StrEnum):
    System = "system"
    User = "user"
    Assistant = "assistant"


class Message(Struct):
    role: Role
    content: str


    @classmethod
    def user(cls, content: str) -> Message:
        return cls(role=Role.User, content=content)


    @classmethod
    def system(cls, content: str) -> Message:
        return cls(role=Role.System, content=content)


    @classmethod
    def assistant(cls, content: str) -> Message:
        return cls(role=Role.Assistant, content=content)


DEFAULT_INSTRUCTION = "You are a helpful assistant."


class Preset(enum.StrEnum):
    Predictable = "predictable"
    Neutral = "neutral"
    Creative = "creative"


class Thread(Struct):
    messages: list[Message]
    instruction: str


    def user(self, prompt: str) -> Thread:
        message = Message.user(prompt)
        self.messages.append(message)
        return self


    async def assistant(
        self,
        llm: LLM,
        preset: Preset = Preset.Neutral,
    ) -> str:
        response = await llm.answer(
            thread=self,
            preset=preset,
        )

        message = Message.assistant(response)
        self.messages.append(message)

        return response


    async def structured(
        self,
        llm: LLM,
        model: type[T],
        preset: Preset = Preset.Neutral,
    ) -> T:
        response = await llm.answer_structured(
            thread=self,
            model=model,
            preset=preset,
        )

        return response


    @classmethod
    def create(
        cls,
        prompt: str | None = None,
        instruction: str = DEFAULT_INSTRUCTION,
    ) -> Thread:
        return cls(
            messages=[Message.user(prompt)] if prompt is not None else [],
            instruction=instruction,
        )


T = t.TypeVar("T")
P = t.ParamSpec("P")


class LLM(ABC):
    @abstractmethod
    async def generate_text_response(
        self,
        thread: Thread,
        preset: Preset,
    ) -> str:
        """
        Generate a response to a thread. Returns the response as a string.
        """


    @abstractmethod
    async def generate_json_response(
        self,
        thread: Thread,
        preset: Preset,
    ) -> dict[str, t.Any]:
        """
        Generate a response to a thread that is a valid JSON object.
        Returns it as a dictionary.
        """


    @abstractmethod
    async def generate_structured_response(
        self,
        thread: Thread,
        model: type[T],
        preset: Preset,
    ) -> T:
        """
        Generate a structured response to a thread validated by the given
        Pydantic model. Returns the response as an instance of the model.
        """


    def _init_thread(
        self,
        prompt: str | None = None,
        instruction: str | None = None,
        thread: Thread | None = None,
    ) -> Thread:
        if thread is None:
            if instruction is None:
                instruction = DEFAULT_INSTRUCTION

            if prompt is None:
                raise ValueError("Prompt must be provided if thread is None.")

            thread = Thread.create(prompt=prompt, instruction=instruction)
        else:
            if instruction is not None:
                raise ValueError("Provide either an instruction or a thread.")

            if prompt is not None:
                thread.messages.append(Message.user(prompt))

        return thread


    async def answer(
        self,
        prompt: str | None = None,
        *,
        instruction: str | None = None,
        thread: Thread | None = None,
        preset: Preset = Preset.Neutral,
    ) -> str:
        """
        High-level interface to `generate_text_response`.
        Returns the response as a string. If append if True,
        the response is appended to the given thread.
        """
        thread = self._init_thread(prompt, instruction, thread)

        response = await self.generate_text_response(thread, preset)

        return response


    async def answer_json(
        self,
        prompt: str | None = None,
        *,
        instruction: str | None = None,
        thread: Thread | None = None,
        preset: Preset = Preset.Neutral,
    ) -> dict[str, t.Any]:
        """
        High-level interface to `generate_json_response`.
        Returns the response as a dictionary. Does not modify the given thread.
        """
        thread = self._init_thread(prompt, instruction, thread)

        response = await self.generate_json_response(thread, preset)

        return response


    async def answer_structured(
        self,
        model: type[T],
        prompt: str | None = None,
        *,
        instruction: str | None = None,
        thread: Thread | None = None,
        preset: Preset = Preset.Neutral,
    ) -> T:
        """
        High-level interface to `generate_structured_response`.
        Returns the response as an instance of the given Pydantic model.
        """
        thread = self._init_thread(prompt, instruction, thread)

        response = await self.generate_structured_response(thread, model, preset)

        return response


    def function(
        self,
        *,
        thread: Thread | None = None,
        preset: Preset = Preset.Neutral,
        reason: bool = False,
        cache: bool | int = False,
    ) -> t.Callable[
        [t.Callable[P, T]],
        t.Callable[P, t.Coroutine[t.Any, t.Any, T]],
    ]:

        def decorator(
            f: t.Callable[P, T],
        ) -> t.Callable[P, t.Coroutine[t.Any, t.Any, T]]:
            signature = inspect.signature(f)

            # Get parameter types (from type hints) and actual values
            type_hints = t.get_type_hints(f)
            param_types = {
                k: v
                for k, v in type_hints.items()
                if k != "return"
            }

            # format argumnets like python type hints
            params: list[str] = []
            for name, type_ in param_types.items():
                params.append(f"{name}: {type_.__name__}")
            params_type_hint = ", ".join(params)

            class Unset:
                pass

            return_type: type[T] = type_hints.get("return", Unset)

            if return_type is Unset:
                message = "Return type must be specified."
                raise ValueError(message)

            if inspect.isclass(return_type) and \
                issubclass(return_type, Struct):
                return_type_hint = ""

            else:
                return_type_hint = f" -> {return_type.__name__}"

            if f.__doc__ is not None:
                instruction = f.__doc__
            else:
                instruction = f"Your task is to compute the function {f.__name__}({params_type_hint}){return_type_hint}." # noqa: E501

            async def implementation(*args: P.args, **kwargs: P.kwargs) -> T:
                bound_arguments = signature.bind(*args, **kwargs)
                bound_arguments.apply_defaults()

                values: list[str] = []
                for name, value in bound_arguments.arguments.items():
                    if inspect.isclass(param_types[name]):
                        if issubclass(param_types[name], Struct):
                            values.append(
                                f"{name} = {msgspec.json.encode(value)}",
                            )
                        else:
                            values.append(f"{name} = {value.__repr__()}")
                    else:
                        values.append(f"{name} = {value.__repr__()}")

                prompt = f"{f.__name__}({'\n'.join(values)})"

                nonlocal thread
                if thread is None:
                    thread = Thread.create(instruction=instruction)

                thread.user(prompt)

                if reason:
                    await thread.assistant(self, preset=preset)

                if inspect.isclass(return_type) and \
                    issubclass(return_type, Struct):

                    return await thread.structured(
                        llm=self,
                        model=return_type,
                        preset=preset,
                    )

                output = msgspec.defstruct(
                    name="Output",
                    fields=[("result", return_type)],
                )
                response = await thread.structured(
                    llm=self,
                    model=output,
                    preset=preset,
                )
                return response.result # type: ignore

            if isinstance(cache, bool):
                if cache:
                    return lru_cache(maxsize=128)(implementation)

                return functools.wraps(f)(implementation)

            return lru_cache(maxsize=cache)(implementation)

        return decorator
