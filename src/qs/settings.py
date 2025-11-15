from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import msgspec
from msgspec import Struct

DEFAULT_CONFIG_PATH = "~/.qs/config.toml"


def load_settings[T: Struct](schema: type[T]) -> T:
    path = os.environ.get("QS_CONFIG", DEFAULT_CONFIG_PATH)
    absolute = Path(path).expanduser()

    if not absolute.exists():
        return schema()

    try:
        with absolute.open() as f:
            data = f.read()
            obj = msgspec.toml.decode(data)
            config = msgspec.convert(obj, type=schema)
    except Exception:
        logging.exception(f"Configuration file at '{absolute}' is invalid.")
        sys.exit(-1)

    return config
