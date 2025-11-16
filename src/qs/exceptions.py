from __future__ import annotations

import re
import typing as t
from dataclasses import dataclass

from litestar.status_codes import (
    HTTP_200_OK,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
    HTTP_500_INTERNAL_SERVER_ERROR,
    HTTP_503_SERVICE_UNAVAILABLE,
    HTTP_502_BAD_GATEWAY,
)


__all__ = [
    "Error",
    "ErrorMeta",
    "BadRequestError",
    "NotFoundError",
    "ConflictError",
    "ServiceUnavailableError",
    "NotImplementedError",
    "UnauthorizedError",
    "ForbiddenError",
    "UpstreamError",
    "PlayerNotFoundError",
    "PlayerAlreadyExistsError",
    "dataclass",
    "HTTP_200_OK",
    "HTTP_400_BAD_REQUEST",
    "HTTP_401_UNAUTHORIZED",
    "HTTP_403_FORBIDDEN",
    "HTTP_404_NOT_FOUND",
    "HTTP_409_CONFLICT",
    "HTTP_500_INTERNAL_SERVER_ERROR",
    "HTTP_503_SERVICE_UNAVAILABLE",
]


def format_error_name(cls: str) -> str:
    snake = re.sub(r"(?<!^)(?=[A-Z])", "_", cls).lower()
    return snake.replace("_error", "")


class ErrorMeta(type):
    _error_name_map: dict[str, str] = {}
    _error_class_map: dict[str, ErrorMeta] = {}
    _error_status_map: dict[str, int] = {}
    _error_detail_map: dict[str, str] = {}

    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, t.Any],
        **kwargs,
    ):
        new = super().__new__(cls, name, bases, namespace)

        error_name = format_error_name(name)

        abstract = kwargs.get("abstract")
        if abstract is True:
            return new

        if error_name in cls._error_name_map:
            raise ValueError(f"Duplicate error name: {error_name}")

        cls._error_name_map[name] = error_name
        cls._error_class_map[error_name] = new

        status_code = kwargs.get("status_code")
        if isinstance(status_code, int):
            cls._error_status_map[error_name] = status_code
        else:
            cls._error_status_map[error_name] = 500

        detail = namespace.get("__doc__")
        if isinstance(detail, str):
            cls._error_detail_map[error_name] = detail

        return new


    @classmethod
    def reconstruct(cls, body: t.Any) -> Error:
        try:
            error_name = body["error"]
            error_class = cls._error_class_map[error_name]
            return error_class(**body)
        except:
            return UpstreamError(details=body)


class Error(Exception, metaclass=ErrorMeta, abstract=True):
    def __post_init__(self):
        self.args = (self.__dict__,)


class BadRequestError(Error, status_code=HTTP_400_BAD_REQUEST):
    """The request could not be understood by the server."""


class NotFoundError(Error, status_code=HTTP_404_NOT_FOUND):
    """The requested resource was not found."""


class ConflictError(Error, status_code=HTTP_409_CONFLICT):
    """Conflict with the current state of the target resource."""


class ServiceUnavailableError(Error, status_code=HTTP_503_SERVICE_UNAVAILABLE):
    """The server is currently unable to handle the request."""


class NotImplementedError(Error, status_code=HTTP_500_INTERNAL_SERVER_ERROR):
    """The requested operation is not implemented."""


class UnauthorizedError(Error, status_code=HTTP_401_UNAUTHORIZED):
    """Client is not authorized to perform this operation."""


class ForbiddenError(Error, status_code=HTTP_403_FORBIDDEN):
    """Client is forbidden from performing this operation."""


@dataclass
class UpstreamError(Error, status_code=HTTP_502_BAD_GATEWAY):
    """An error was encountered while processing the request."""

    details: dict[str, t.Any]


@dataclass
class PlayerNotFoundError(Error, status_code=HTTP_404_NOT_FOUND):
    """The requested player was not found in the session."""

    session_id: str
    username: str


@dataclass
class PlayerAlreadyExistsError(Error, status_code=HTTP_409_CONFLICT):
    """The player with the given username already exists in the session."""

    session_id: str
    username: str


@dataclass
class UnderflowError(Error, status_code=HTTP_400_BAD_REQUEST):
    """An attempt was made to reduce a position below zero."""

    symbol: str
    attempted_reduction: int
    current_size: int
