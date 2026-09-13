"""Executable module entrypoint for python -m automation_master."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
