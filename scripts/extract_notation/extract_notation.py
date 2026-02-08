#!/usr/bin/env python3
"""Extract raw macro and indexed-symbol usage from TeX files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_notation import run_checks  # type: ignore


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tex-root", type=Path, required=True)
    parser.add_argument("--notation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    _summary, raw = run_checks(args.tex_root, args.notation)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
