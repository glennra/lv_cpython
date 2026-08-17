from pathlib import Path

import pytest


INTEGRATION_DIR = Path(__file__).resolve().parent


def pytest_collection_modifyitems(items):
    """Mark every test collected from this directory as integration."""
    marker = pytest.mark.integration
    for item in items:
        if INTEGRATION_DIR in Path(item.path).resolve().parents:
            item.add_marker(marker)
