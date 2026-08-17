"""Run one pytest lifetime case repeatedly inside an isolated process."""

import argparse
import os
from pathlib import Path

import pytest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("node_id")
    parser.add_argument("--repetitions", type=int, default=1)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    os.chdir(root)
    os.environ["LV_SKIP_REGENERATION"] = "1"

    for iteration in range(args.repetitions):
        result = pytest.main(["-q", args.node_id])
        if result != pytest.ExitCode.OK:
            raise SystemExit(
                f"{args.node_id} failed on repetition {iteration + 1}"
            )


if __name__ == "__main__":
    main()
