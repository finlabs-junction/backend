from __future__ import annotations

import msgspec

from qs.contrib.litestar import AppSettings
from qs.contrib.openai.settings import OpenAISettings


class Settings(AppSettings):
    openai: OpenAISettings = msgspec.field(
        default_factory=OpenAISettings,
    )
