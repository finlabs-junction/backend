from __future__ import annotations

import typing as t

from qs.exceptions import ConflictError, Error, ErrorMeta, NotFoundError

from litestar import Response
from litestar.repository.exceptions import (
    NotFoundError as RepositoryNotFoundError,
)
from litestar.repository.exceptions import (
    RepositoryError,
)

if t.TYPE_CHECKING:
    from litestar import Request


__all__ = ["Error", "exception_handler"]


def exception_handler(
    request: Request,
    exc: Error | RepositoryError,
) -> Response:
    if isinstance(exc, RepositoryNotFoundError):
        exc = NotFoundError()
    elif isinstance(exc, RepositoryError):
        exc = ConflictError()

    error_name = ErrorMeta._error_name_map[exc.__class__.__name__]
    status_code = ErrorMeta._error_status_map[error_name]

    content = {
        "status_code": status_code,
        "error": error_name,
    }

    detail = ErrorMeta._error_detail_map.get(error_name)
    if detail is not None:
        content["detail"] = detail

    if exc.__dict__ != {}:
        content["extra"] = exc.__dict__

    return Response(
        content=content,
        status_code=status_code,
    )
