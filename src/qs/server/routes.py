from __future__ import annotations

import typing as t

from qs.contrib.litestar import *
from qs.server import get_settings
from qs.server.exceptions import *
from qs.server.schemas import *
from qs.server.services import *


def get_routes() -> list[ControllerRouterHandler]:
    return []
