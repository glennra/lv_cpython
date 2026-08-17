from pathlib import Path

import pytest


ACCEPTANCE_DIR = Path(__file__).resolve().parent


def pytest_collection_modifyitems(items):
    marker = pytest.mark.acceptance
    for item in items:
        if ACCEPTANCE_DIR in Path(item.path).resolve().parents:
            item.add_marker(marker)
