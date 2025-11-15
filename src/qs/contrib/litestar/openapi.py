from __future__ import annotations

import typing as t

from qs.contrib.litestar.constants import OPENAPI_ENDPOINT

from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.openapi.spec import Server

if t.TYPE_CHECKING:
    from qs.contrib.litestar.settings import AppSettings


def create_openapi_config(settings: AppSettings) -> OpenAPIConfig:
    default_urls = [
        "/",
        "http://localhost:8000",
    ]

    servers = [
        Server(url=url) for url in default_urls
    ]

    return OpenAPIConfig(
        title=settings.api.app_name,
        version="0.1.0",
        create_examples=False,
        components=[],
        security=[],
        use_handler_docstrings=True,
        render_plugins=[ScalarRenderPlugin()],
        path=OPENAPI_ENDPOINT,
        servers=servers,
    )
