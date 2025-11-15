from __future__ import annotations

from litestar import Controller, get


class HealthController(Controller):
    path = "/health"
    tags = ["Health"]


    @get("/liveness")
    async def health_liveness_check(self) -> None:
        pass


    @get("/readiness")
    async def health_readiness_check(self) -> None:
        pass
