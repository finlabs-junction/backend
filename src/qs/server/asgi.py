from __future__ import annotations

from qs.server import factory
from qs.server.dependencies import get_dependencies
from qs.server.routes import get_routes

routes = get_routes()
factory.add_routes(routes)

dependencies = get_dependencies()
factory.add_dependencies(dependencies)

app = factory.create_app()
