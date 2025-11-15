from __future__ import annotations

import typing as t

from qs.nlp import Embeddings

from openai import AsyncOpenAI

__all__ = [
    "OpenAIEmbeddings",
    "create_flagship_openai_embeddings",
    "create_small_openai_embeddings",
]


class OpenAIEmbeddings(Embeddings):
    def __init__(
        self,
        client: AsyncOpenAI,
        model: str,
    ) -> None:
        self._client = client
        self._model = model


    @t.override
    async def create(self, input: str) -> list[float]:
        response = await self._client.embeddings.create(
            input=input,
            model=self._model,
        )
        return response.data[0].embedding


def create_flagship_openai_embeddings(client: AsyncOpenAI) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        client=client,
        model="text-embedding-3-large",
    )


def create_small_openai_embeddings(client: AsyncOpenAI) -> OpenAIEmbeddings:
    return OpenAIEmbeddings(
        client=client,
        model="text-embedding-3-small",
    )
