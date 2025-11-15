from __future__ import annotations

import typing as t
from datetime import date, datetime
from uuid import UUID

from advanced_alchemy.base import (
    DefaultBase as _DefaultBase,
)
from advanced_alchemy.base import (
    UUIDAuditBase as _UUIDAuditBase,
)
from advanced_alchemy.base import (
    UUIDBase as _UUIDBase,
)
from qs.contrib.sqlalchemy.engine import create_engine
from qs.contrib.sqlalchemy.settings import SQLAlchemySettings

from sqlalchemy import JSON, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship


class _TypeAnnotationMixin:
    __abstract__ = True

    type_annotation_map = {
        str: String,
        t.Any: JSON().with_variant(JSONB, "postgresql"),
    }


class DefaultBase(_DefaultBase, _TypeAnnotationMixin):
    __abstract__ = True


class UUIDBase(_UUIDBase, _TypeAnnotationMixin):
    __abstract__ = True


class UUIDAuditBase(_UUIDAuditBase, _TypeAnnotationMixin):
    __abstract__ = True


__all__ = [
    "t",
    "UUID",
    "date",
    "datetime",
    "DefaultBase",
    "UUIDBase",
    "UUIDAuditBase",
    "Mapped",
    "mapped_column",
    "relationship",
    "UniqueConstraint",
    "String",
    "Text",
    "JSON",
    "ForeignKey",
    "JSONB",
    "ENUM",
    "SQLAlchemySettings",
    "create_engine",
]
