from __future__ import annotations

import typing as t


def create_cli(app: str) -> t.Callable[[], None]:
    def run_cli() -> None:
        """Application Entrypoint."""
        import os
        import sys
        from pathlib import Path

        current_path = Path(__file__).parent.parent.resolve()
        sys.path.append(str(current_path))
        os.environ.setdefault("LITESTAR_APP", app)
        try:
            from litestar.__main__ import run_cli as run_litestar_cli

        except ImportError as exc:
            print(  # noqa: T201
                "Could not load required libraries. ",
                "Please check your installation and make sure you activated any necessary virtual environment",
            )
            print(exc)  # noqa: T201
            sys.exit(1)
        run_litestar_cli()

    return run_cli
