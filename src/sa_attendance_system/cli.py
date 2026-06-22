from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .db import database_summary, init_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sa-attendance",
        description="Local-first command tools for SA Attendance System.",
    )
    parser.add_argument("--version", action="version", version=__version__)

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize the local database.")
    init_parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/attendance.sqlite"),
        help="SQLite database path.",
    )

    info_parser = subparsers.add_parser("info", help="Show database table counts.")
    info_parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/attendance.sqlite"),
        help="SQLite database path.",
    )

    return parser


def main() -> None:
    args = build_parser().parse_args()

    if args.command == "init":
        init_database(args.db)
        print(f"Initialized SA Attendance database at {args.db}")
        return

    if args.command == "info":
        summary = database_summary(args.db)
        for table, count in summary.items():
            print(f"{table}: {count}")
        return


if __name__ == "__main__":
    main()

