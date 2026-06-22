from __future__ import annotations

import sqlite3
from importlib import resources
from pathlib import Path


def load_schema() -> str:
    schema_path = Path(__file__).resolve().parents[2] / "db" / "schema.sql"
    if schema_path.exists():
        return schema_path.read_text(encoding="utf-8")

    return (
        resources.files("sa_attendance_system")
        .joinpath("resources/schema.sql")
        .read_text(encoding="utf-8")
    )


def init_database(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript(load_schema())
        conn.commit()


def database_summary(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        tables = [
            "students",
            "classes",
            "class_sessions",
            "attendance_records",
            "attendance_observations",
            "face_profiles",
            "devices",
            "memory_facts",
            "skill_runs",
            "people",
            "person_face_images",
            "captures",
            "face_observations",
            "recognition_candidates",
        ]
        return {
            table: conn.execute(f"SELECT COUNT(*) AS count FROM {table}").fetchone()[
                "count"
            ]
            for table in tables
        }
