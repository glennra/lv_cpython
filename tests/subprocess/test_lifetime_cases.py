import os
from pathlib import Path
import subprocess
import sys

import pytest


CASES = [
    "tests/lifetime/test_buttonmatrix_map_lifetime.py::"
    "test_buttonmatrix_map_survives_collection",
    "tests/lifetime/test_keyboard_map_lifetime.py::"
    "test_keyboard_map_survives_collection",
    "tests/lifetime/test_style_lifetime.py::"
    "test_attached_style_survives_collection",
    "tests/lifetime/test_canvas_lifetime.py::"
    "test_canvas_buffer_survives_collection",
    "tests/lifetime/test_callback_lifetime.py::"
    "test_event_callback_and_user_data_survive_collection",
    "tests/lifetime/test_callback_lifetime.py::"
    "test_timer_callback_survives_collection",
    "tests/lifetime/test_fs_handle_lifetime_collection.py::"
    "test_filesystem_handle_survives_collection",
    "tests/lifetime/test_struct_buffer_lifetime.py::"
    "test_image_descriptor_buffer_survives_collection",
]
RUNNER = Path(__file__).with_name("run_lifetime_case.py")


def _run_case(node_id, repetitions):
    result = subprocess.run(
        [
            sys.executable,
            str(RUNNER),
            node_id,
            "--repetitions",
            str(repetitions),
        ],
        capture_output=True,
        text=True,
        timeout=max(15, repetitions * 5),
        env={**os.environ, "LV_SKIP_REGENERATION": "1"},
    )
    assert result.returncode == 0, (
        f"{node_id} exited with {result.returncode}\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )


@pytest.mark.subprocess
@pytest.mark.parametrize("node_id", CASES)
def test_lifetime_case_in_subprocess(node_id):
    _run_case(node_id, 1)


@pytest.mark.subprocess
@pytest.mark.stress
@pytest.mark.parametrize("node_id", CASES)
def test_lifetime_case_stress(node_id):
    repetitions = int(os.environ.get("LV_TEST_REPETITIONS", "100"))
    _run_case(node_id, repetitions)
