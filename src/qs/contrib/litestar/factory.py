from __future__ import annotations

import typing as t
from contextlib import AbstractAsyncContextManager, asynccontextmanager

from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar_saq import QueueConfig
from qs.contrib.litestar.dependencies import *
from qs.contrib.litestar.domain.system import HealthController
from qs.contrib.litestar.exception_handler import exception_handler
from qs.contrib.litestar.openapi import create_openapi_config
from qs.contrib.litestar.plugins import (
    create_cors_config,
    create_saq_plugin,
)
from qs.contrib.litestar.settings import AppSettings
from qs.contrib.redis.client import create_redis_client
from qs.contrib.sqlalchemy.settings import create_sqlalchemy_config
from qs.exceptions import Error
from qs.settings import load_settings

from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.config.response_cache import (
    ResponseCacheConfig,
    default_cache_key_builder,
)
from litestar.di import Provide
from litestar.plugins import PluginProtocol
from litestar.repository.exceptions import RepositoryError
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry
from litestar.types import ControllerRouterHandler, Middleware
from msgspec import Struct

if t.TYPE_CHECKING:
    from litestar import Request


LifespanContextManager = t.Union[
    t.Callable[[Litestar], AbstractAsyncContextManager],
    AbstractAsyncContextManager,
]


SETTINGS_DEPENDENCY_KEY = "settings"
FILTERS_DEPENDENCY_KEY = "filters"
CREATED_FILTER_DEPENDENCY_KEY = "created_filter"
ID_FILTER_DEPENDENCY_KEY = "id_filter"
LIMIT_OFFSET_DEPENDENCY_KEY = "limit_offset"
UPDATED_FILTER_DEPENDENCY_KEY = "updated_filter"
ORDER_BY_DEPENDENCY_KEY = "order_by"
SEARCH_FILTER_DEPENDENCY_KEY = "search_filter"


class AppFactory[T: Struct]:
    def __init__(
        self, 
        settings_type: type[T],
        app_settings_getter,
    ) -> None:
        self._settings = load_settings(settings_type)
        self._app_settings = app_settings_getter(self._settings)
        self._route_handlers: list[ControllerRouterHandler] = [
            HealthController,
        ]
        self._dependencies: dict[str, Provide] = {
            SETTINGS_DEPENDENCY_KEY: Provide(
                lambda: self._settings,
                sync_to_thread=False,
            ),
            LIMIT_OFFSET_DEPENDENCY_KEY: Provide(
                provide_limit_offset_pagination,
                sync_to_thread=False,
            ),
            UPDATED_FILTER_DEPENDENCY_KEY: Provide(
                provide_updated_filter,
                sync_to_thread=False,
            ),
            CREATED_FILTER_DEPENDENCY_KEY: Provide(
                provide_created_filter,
                sync_to_thread=False,
            ),
            ID_FILTER_DEPENDENCY_KEY: Provide(
                provide_id_filter,
                sync_to_thread=False,
            ),
            SEARCH_FILTER_DEPENDENCY_KEY: Provide(
                provide_search_filter,
                sync_to_thread=False,
            ),
            ORDER_BY_DEPENDENCY_KEY: Provide(
                provide_order_by,
                sync_to_thread=False,
            ),
            FILTERS_DEPENDENCY_KEY: Provide(
                provide_filter_dependencies,
                sync_to_thread=False,
            ),
        }
        self._sqla_config = create_sqlalchemy_config(self._app_settings.sqlalchemy)
        self._redis = create_redis_client(self._app_settings.redis)
        self._plugins: list[PluginProtocol] = [
            SQLAlchemyPlugin(self._sqla_config),
        ]
        self._signature_namespace: dict[str, t.Any] = {}
        self._middleware: list[Middleware] = []

        @asynccontextmanager
        async def lifespan(app: Litestar):
            yield
            await self._redis.aclose()

        self._lifespan: list[LifespanContextManager] = [lifespan]
        self._queue_configs: list[QueueConfig] = []


    def add_route(
        self,
        route_handler: ControllerRouterHandler,
    ) -> None:
        self._route_handlers.append(route_handler)


    def add_routes(
        self,
        route_handlers: t.Iterable[ControllerRouterHandler],
    ) -> None:
        self._route_handlers.extend(route_handlers)


    def add_dependency(self, key: str, dependency: Provide) -> None:
        self._dependencies[key] = dependency


    def add_dependencies(self, dependencies: t.Mapping[str, Provide]) -> None:
        self._dependencies.update(dependencies)


    def add_lifespan(self, lifespan: LifespanContextManager) -> None:
        self._lifespan.append(lifespan)


    def add_plugin(self, plugin: PluginProtocol) -> None:
        self._plugins.append(plugin)


    def add_plugins(self, plugins: t.Iterable[PluginProtocol]) -> None:
        self._plugins.extend(plugins)


    def add_type(self, key: str, value: t.Any) -> None:
        self._signature_namespace[key] = value


    def add_types(self, types: t.Mapping[str, t.Any]) -> None:
        self._signature_namespace.update(types)


    def add_queue(self, config: QueueConfig) -> None:
        self._queue_configs.append(config)


    def add_queues(self, configs: t.Iterable[QueueConfig]) -> None:
        self._queue_configs.extend(configs)

    
    def add_middleware(self, middleware: Middleware) -> None:
        self._middleware.append(middleware)


    def cache_key_builder(self, request: Request) -> str:
        default_key = default_cache_key_builder(request)
        return f"{self._app_settings.api.app_name}:{default_key}"


    def create_settings_getter(self) -> t.Callable[[], T]:
        return lambda: self._settings


    def create_session_getter(self):
        return lambda: self._sqla_config.get_session()


    def create_app(self) -> Litestar:
        return Litestar(
            path="/api",
            debug=self._app_settings.api.debug,
            cors_config=create_cors_config(self._app_settings.api),
            compression_config=CompressionConfig(
                backend="brotli",
                exclude=["/saq"],
            ),
            openapi_config=create_openapi_config(self._app_settings),
            plugins=self._plugins + [
                create_saq_plugin(
                    settings=self._app_settings.saq,
                    queue_configs=self._queue_configs,
                ),
            ],
            route_handlers=self._route_handlers,
            exception_handlers={
                Error: exception_handler,
                RepositoryError: exception_handler,
            },
            dependencies=self._dependencies,
            lifespan=self._lifespan,
            response_cache_config=ResponseCacheConfig(
                default_expiration=self._app_settings.api.cache_expiration,
                key_builder=self.cache_key_builder,
            ),
            stores=StoreRegistry(
                default_factory=lambda name: RedisStore(
                    self._redis,
                    namespace=f"{self._app_settings.api.app_name}:{name}",
                ),
            ),
            signature_namespace=self._signature_namespace,
            middleware=self._middleware,
        )
