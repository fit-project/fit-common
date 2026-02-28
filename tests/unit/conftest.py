from pathlib import Path
import sys

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]
repo_root_str = str(REPO_ROOT)
if sys.path[0] != repo_root_str:
    try:
        sys.path.remove(repo_root_str)
    except ValueError:
        pass
    sys.path.insert(0, repo_root_str)


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    unit_marker = pytest.mark.unit
    for item in items:
        if "/tests/unit/" in str(item.fspath):
            item.add_marker(unit_marker)
