from __future__ import annotations

import typing as t
from datetime import date, datetime, timezone
from uuid import UUID
from enum import Enum, StrEnum

import msgspec
from msgspec import Struct as _Struct
from msgspec import field


class Struct(_Struct, rename="camel"):
    pass


__all__ = [
    "t",
    "UUID",
    "date",
    "datetime",
    "timezone",
    "Enum",
    "StrEnum",
    "msgspec",
    "Struct",
    "field",
]
