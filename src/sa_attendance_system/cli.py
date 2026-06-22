from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import __version__
from .api import make_server
from .db import database_summary, init_database
from .service import SAAttendanceService


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

    serve_parser = subparsers.add_parser("serve", help="Start the local Face API.")
    serve_parser.add_argument("--host", default="127.0.0.1", help="API bind host.")
    serve_parser.add_argument("--port", type=int, default=8765, help="API port.")
    add_runtime_args(serve_parser)

    create_person_parser = subparsers.add_parser(
        "create-person",
        help="Create a student, teacher, or staff identity.",
    )
    create_person_parser.add_argument("display_name")
    create_person_parser.add_argument(
        "--type",
        default="student",
        choices=["student", "teacher", "staff", "unknown"],
        help="Person type.",
    )
    create_person_parser.add_argument("--external-id")
    create_person_parser.add_argument("--notes")
    add_runtime_args(create_person_parser)

    enroll_parser = subparsers.add_parser(
        "enroll-face",
        help="Enroll one face image for a person.",
    )
    enroll_parser.add_argument("person_id")
    enroll_parser.add_argument("image_path", type=Path)
    enroll_parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Do not use the whole image if no face is detected.",
    )
    add_runtime_args(enroll_parser)

    recognize_parser = subparsers.add_parser(
        "recognize",
        help="Recognize people in an image.",
    )
    recognize_parser.add_argument("image_path", type=Path)
    recognize_parser.add_argument("--threshold", type=float, default=0.95)
    recognize_parser.add_argument("--review-threshold", type=float, default=0.70)
    recognize_parser.add_argument("--max-candidates", type=int, default=5)
    recognize_parser.add_argument(
        "--fallback-to-full-image",
        action="store_true",
        help="Treat the whole image as one face if detection finds no faces.",
    )
    add_runtime_args(recognize_parser)

    stats_parser = subparsers.add_parser("stats", help="Show Face API object counts.")
    add_runtime_args(stats_parser)

    return parser


def add_runtime_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("data/attendance.sqlite"),
        help="SQLite database path.",
    )
    parser.add_argument(
        "--media-dir",
        type=Path,
        default=Path("data/media"),
        help="Local media storage directory.",
    )


def print_json(payload: dict | list) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


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

    if args.command == "serve":
        server = make_server(
            host=args.host,
            port=args.port,
            db_path=args.db,
            media_dir=args.media_dir,
        )
        print(f"SA Attendance API running at http://{args.host}:{args.port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nSA Attendance API stopped.")
        return

    service = SAAttendanceService(db_path=args.db, media_dir=args.media_dir)

    if args.command == "create-person":
        print_json(
            service.create_person(
                display_name=args.display_name,
                person_type=args.type,
                external_id=args.external_id,
                notes=args.notes,
            )
        )
        return

    if args.command == "enroll-face":
        print_json(
            service.enroll_face(
                person_id=args.person_id,
                image_bytes=args.image_path.read_bytes(),
                filename=args.image_path.name,
                fallback_to_full_image=not args.no_fallback,
            )
        )
        return

    if args.command == "recognize":
        print_json(
            service.recognize_image(
                image_bytes=args.image_path.read_bytes(),
                filename=args.image_path.name,
                threshold=args.threshold,
                review_threshold=args.review_threshold,
                max_candidates=args.max_candidates,
                fallback_to_full_image=args.fallback_to_full_image,
            )
        )
        return

    if args.command == "stats":
        print_json(service.stats())
        return


if __name__ == "__main__":
    main()
