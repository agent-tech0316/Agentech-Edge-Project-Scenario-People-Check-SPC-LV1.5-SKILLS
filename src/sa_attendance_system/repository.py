from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .db import init_database
from .utils import new_id, utc_now


def dumps(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def loads(value: str | None, default: Any = None) -> Any:
    if value is None:
        return default
    return json.loads(value)


class Repository:
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        init_database(self.db_path)

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def create_person(
        self,
        display_name: str,
        person_type: str = "student",
        external_id: str | None = None,
        notes: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        person_id = new_id("person")
        now = utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO people (
                  id, external_id, display_name, person_type, notes, metadata_json,
                  created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    person_id,
                    external_id,
                    display_name,
                    person_type,
                    notes,
                    dumps(metadata or {}),
                    now,
                    now,
                ),
            )
            conn.commit()
        return self.get_person(person_id)

    def get_person(self, person_id: str) -> dict:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM people WHERE id = ?",
                (person_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Person not found: {person_id}")
        return self.row_to_person(row)

    def list_people(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT p.*,
                  (SELECT COUNT(*) FROM person_face_images f WHERE f.person_id = p.id)
                    AS face_image_count
                FROM people p
                ORDER BY p.display_name COLLATE NOCASE
                """
            ).fetchall()
        return [self.row_to_person(row) for row in rows]

    def create_media_asset(
        self,
        file_path: Path,
        source_kind: str,
        captured_at: str,
        mime_type: str,
        sha256: str,
        metadata: dict | None = None,
    ) -> dict:
        media_id = new_id("media")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO media_assets (
                  id, source_kind, file_path, mime_type, captured_at, sha256,
                  metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    media_id,
                    source_kind,
                    str(file_path),
                    mime_type,
                    captured_at,
                    sha256,
                    dumps(metadata or {}),
                ),
            )
            conn.commit()
        return {"id": media_id, "file_path": str(file_path)}

    def add_person_face_image(
        self,
        person_id: str,
        media_asset_id: str,
        embedding_model: str,
        embedding: list[float],
        face_box: dict,
        quality_score: float,
        source_observation_id: str | None = None,
    ) -> dict:
        face_image_id = new_id("faceimg")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO person_face_images (
                  id, person_id, media_asset_id, source_observation_id,
                  embedding_model, embedding_json, face_box_json, quality_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    face_image_id,
                    person_id,
                    media_asset_id,
                    source_observation_id,
                    embedding_model,
                    dumps(embedding),
                    dumps(face_box),
                    quality_score,
                ),
            )
            conn.commit()
        return {"id": face_image_id, "person_id": person_id}

    def reference_embeddings(self) -> list[dict]:
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                  f.id AS face_image_id,
                  f.embedding_model,
                  f.embedding_json,
                  f.quality_score,
                  p.id AS person_id,
                  p.external_id,
                  p.display_name,
                  p.person_type
                FROM person_face_images f
                JOIN people p ON p.id = f.person_id
                WHERE p.status = 'active'
                """
            ).fetchall()
        return [
            {
                "face_image_id": row["face_image_id"],
                "embedding_model": row["embedding_model"],
                "embedding": loads(row["embedding_json"], []),
                "quality_score": row["quality_score"],
                "person": {
                    "id": row["person_id"],
                    "external_id": row["external_id"],
                    "display_name": row["display_name"],
                    "person_type": row["person_type"],
                },
            }
            for row in rows
        ]

    def create_capture(
        self,
        media_asset_id: str,
        captured_at: str,
        source_kind: str = "api_upload",
        source_label: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        capture_id = new_id("capture")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO captures (
                  id, media_asset_id, source_kind, source_label, captured_at,
                  metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    capture_id,
                    media_asset_id,
                    source_kind,
                    source_label,
                    captured_at,
                    dumps(metadata or {}),
                ),
            )
            conn.commit()
        return {"id": capture_id, "media_asset_id": media_asset_id}

    def add_face_observation(
        self,
        capture_id: str,
        face_index: int,
        face_box: dict,
        quality_score: float,
        embedding_model: str,
        embedding: list[float],
        status: str,
    ) -> dict:
        observation_id = new_id("obs")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO face_observations (
                  id, capture_id, face_index, face_box_json, quality_score,
                  embedding_model, embedding_json, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    observation_id,
                    capture_id,
                    face_index,
                    dumps(face_box),
                    quality_score,
                    embedding_model,
                    dumps(embedding),
                    status,
                ),
            )
            conn.commit()
        return {"id": observation_id, "capture_id": capture_id}

    def add_recognition_candidate(
        self,
        observation_id: str,
        person_id: str | None,
        confidence: float,
        rank: int,
        decision: str,
    ) -> dict:
        candidate_id = new_id("cand")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO recognition_candidates (
                  id, observation_id, person_id, confidence, rank, decision
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (candidate_id, observation_id, person_id, confidence, rank, decision),
            )
            conn.commit()
        return {"id": candidate_id}

    def get_observation_media(self, observation_id: str) -> dict:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                  o.id AS observation_id,
                  o.face_box_json,
                  o.quality_score,
                  c.id AS capture_id,
                  m.id AS media_asset_id,
                  m.file_path
                FROM face_observations o
                JOIN captures c ON c.id = o.capture_id
                JOIN media_assets m ON m.id = c.media_asset_id
                WHERE o.id = ?
                """,
                (observation_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Observation not found: {observation_id}")
        return {
            "observation_id": row["observation_id"],
            "capture_id": row["capture_id"],
            "media_asset_id": row["media_asset_id"],
            "file_path": row["file_path"],
            "face_box": loads(row["face_box_json"], {}),
            "quality_score": row["quality_score"],
        }

    def add_feedback(
        self,
        observation_id: str,
        action: str,
        person_id: str | None = None,
        notes: str | None = None,
    ) -> dict:
        feedback_id = new_id("feedback")
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO recognition_feedback (
                  id, observation_id, action, person_id, notes
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (feedback_id, observation_id, action, person_id, notes),
            )
            if action == "assign" and person_id:
                conn.execute(
                    "UPDATE face_observations SET status = 'assigned' WHERE id = ?",
                    (observation_id,),
                )
            conn.commit()
        return {"id": feedback_id}

    def stats(self) -> dict:
        tables = [
            "people",
            "person_face_images",
            "captures",
            "face_observations",
            "recognition_candidates",
            "recognition_feedback",
        ]
        with self.connect() as conn:
            return {
                table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in tables
            }

    @staticmethod
    def row_to_person(row: sqlite3.Row) -> dict:
        result = {
            "id": row["id"],
            "external_id": row["external_id"],
            "display_name": row["display_name"],
            "person_type": row["person_type"],
            "status": row["status"],
            "notes": row["notes"],
            "metadata": loads(row["metadata_json"], {}),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }
        if "face_image_count" in row.keys():
            result["face_image_count"] = row["face_image_count"]
        return result

