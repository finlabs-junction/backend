from __future__ import annotations

import typing as t

from advanced_alchemy.filters import FilterTypes, LimitOffset
from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from advanced_alchemy.service import (
    OffsetPagination,
    SQLAlchemyAsyncRepositoryService,
)
from litestar_saq import CronJob, QueueConfig, TaskQueues
from saq.job import Job, Status
from saq.types import Context, QueueInfo
from sqlalchemy.ext.asyncio import AsyncSession
from qs.contrib.litestar.dependencies import *
from qs.contrib.litestar.factory import AppFactory
from qs.contrib.litestar.settings import AppSettings

from litestar import (
    Controller,
    delete,
    get,
    patch,
    post,
    put,
)
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.params import Body, Dependency, Parameter
from litestar.types import ControllerRouterHandler

__all__ = [
    "t",
    "Controller",
    "get",
    "post",
    "put",
    "patch",
    "delete",
    "Provide",
    "Parameter",
    "Dependency",
    "Body",
    "ControllerRouterHandler",
    "RequestEncodingType",
    "LimitOffset",
    "FilterTypes",
    "SQLAlchemyAsyncRepository",
    "SQLAlchemyAsyncRepositoryService",
    "OffsetPagination",
    "AsyncSession",
    "Job",
    "Status",
    "Context",
    "QueueInfo",
    "QueueConfig",
    "TaskQueues",
    "CronJob",
    "AppSettings",
    "AppFactory",
    "provide_id_filter",
    "provide_limit_offset_pagination",
    "provide_updated_filter",
    "provide_created_filter",
    "provide_order_by",
    "provide_search_filter",
    "provide_filter_dependencies",
    "create_service_provider",
]
