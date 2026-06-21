from __future__ import annotations

import argparse
import sys
from pathlib import Path

from geosciloop.core.runner import run_config
from geosciloop.core.schema import load_task_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="geosciloop")
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="Run a GeoSciLoop workflow config.")
    run_parser.add_argument("config", help="Path to YAML config.")
    run_parser.add_argument("--offline", action="store_true", help="Force offline mode.")
    run_parser.add_argument("--dry-run", action="store_true", help="Run fixture-backed dry-run planning mode.")
    run_parser.add_argument("--output-dir", help="Override output directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        config = load_task_config(
            args.config,
            offline_override=True if args.offline else None,
            dry_run_override=True if args.dry_run else None,
        )
        if args.output_dir:
            config.output_dir = Path(args.output_dir)
        result = run_config(config)
        print(f"GeoSciLoop run complete: {result.output_dir}")
        print(f"Validation hard failures: {len(result.hard_failures)}")
        return 1 if result.hard_failures else 0

    parser.error(f"Unsupported command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
