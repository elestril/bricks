#!/usr/bin/env python3
"""Pytest entrypoint for repository tests."""

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main(argv: list[str] | None = None) -> None:
    os.chdir(PROJECT_ROOT)
    cli_args = argv if argv is not None else sys.argv[1:]
    pytest_args = ["pythonscad/tests"]
    if cli_args:
        pytest_args.extend(cli_args)
    raise SystemExit(pytest.main(pytest_args))


if __name__ == "__main__":
    main()
