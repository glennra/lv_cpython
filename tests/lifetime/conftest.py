from pathlib import Path

import pytest


LIFETIME_DIR = Path(__file__).resolve().parent


def pytest_collection_modifyitems(items):
    """Mark every test collected from this directory as lifetime."""
    marker = pytest.mark.lifetime
    for item in items:
        if LIFETIME_DIR in Path(item.path).resolve().parents:
            item.add_marker(marker)
