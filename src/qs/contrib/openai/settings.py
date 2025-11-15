from __future__ import annotations

import os

import msgspec
from msgspec import Struct


class OpenAISettings(Struct):
    api_key: str = os.environ.get("QS_OPENAI_API_KEY", "")
    """
    OpenAI API key.
    """


class OpenAISettingsMixin(Struct):
    openai: OpenAISettings = msgspec.field(default_factory=OpenAISettings)
    """
    OpenAI settings.
    """
