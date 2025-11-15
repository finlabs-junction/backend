from __future__ import annotations

from qs.cli import create_cli

cli = create_cli("qs.server.asgi:app")


if __name__ == "__main__":
    cli()
