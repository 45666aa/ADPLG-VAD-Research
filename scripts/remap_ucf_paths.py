#!/usr/bin/env python3
"""Remap hardcoded UCF-Crime I3D list-file prefixes for baseline reproduction."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


OLD_PREFIX = "/data2/Vision_Group/YZW/Datasets/Fourth-Work/UCF-10Crop-WP"
LIST_FILES = (
    Path("list/UCF_Train.list"),
    Path("list/UCF_Test.list"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rewrite only the UCF-Crime I3D path prefix in official list files."
    )
    parser.add_argument(
        "new_prefix",
        help="New UCF-10Crop-WP root path, e.g. /root/autodl-tmp/datasets/UCF-10Crop-WP",
    )
    return parser.parse_args()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines(keepends=True)


def count_prefix(lines: list[str], prefix: str) -> int:
    return sum(line.count(prefix) for line in lines)


def preview_lines(lines: list[str]) -> list[str]:
    if len(lines) <= 6:
        return [line.rstrip("\n") for line in lines]
    return [line.rstrip("\n") for line in lines[:3] + lines[-3:]]


def ensure_inputs_exist() -> None:
    missing = [str(path) for path in LIST_FILES if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required list file(s): " + ", ".join(missing))


def backup_file(path: Path) -> None:
    backup_path = path.with_suffix(path.suffix + ".bak")
    if not backup_path.exists():
        shutil.copy2(path, backup_path)


def remap_file(path: Path, new_prefix: str) -> None:
    original_lines = read_lines(path)
    original_count = len(original_lines)
    old_occurrences = count_prefix(original_lines, OLD_PREFIX)

    print(f"\n{path}")
    print(f"  lines before: {original_count}")
    print(f"  old prefix occurrences before: {old_occurrences}")

    backup_file(path)

    rewritten_lines = [
        line.replace(OLD_PREFIX, new_prefix) if OLD_PREFIX in line else line
        for line in original_lines
    ]
    path.write_text("".join(rewritten_lines), encoding="utf-8")

    final_lines = read_lines(path)
    final_count = len(final_lines)
    final_old_occurrences = count_prefix(final_lines, OLD_PREFIX)

    if final_count != original_count:
        raise RuntimeError(
            f"{path}: line count changed from {original_count} to {final_count}"
        )
    if final_old_occurrences != 0:
        raise RuntimeError(
            f"{path}: old prefix still appears {final_old_occurrences} time(s)"
        )

    print(f"  lines after: {final_count}")
    print("  old prefix occurrences after: 0")
    print("  preview:")
    for line in preview_lines(final_lines):
        print(f"    {line}")


def main() -> None:
    args = parse_args()
    new_prefix = args.new_prefix.rstrip("/")

    ensure_inputs_exist()
    for path in LIST_FILES:
        remap_file(path, new_prefix)


if __name__ == "__main__":
    main()
