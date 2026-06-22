from __future__ import annotations

import shutil
from collections import defaultdict
from pathlib import Path

import cv2

from .repository import Repository
from .utils import (
    guess_mime_type,
    new_id,
    safe_extension,
    sha256_bytes,
    utc_now,
)
from .vision import LocalVisionEngine


class SAAttendanceService:
    def __init__(self, db_path: Path, media_dir: Path):
        self.repo = Repository(Path(db_path))
        self.media_dir = Path(media_dir)
        self.media_dir.mkdir(parents=True, exist_ok=True)
        self.vision = LocalVisionEngine()

    def create_person(
        self,
        display_name: str,
        person_type: str = "student",
        external_id: str | None = None,
        notes: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        return self.repo.create_person(
            display_name=display_name,
            person_type=person_type,
            external_id=external_id,
            notes=notes,
            metadata=metadata,
        )

    def list_people(self) -> list[dict]:
        return self.repo.list_people()

    def enroll_face(
        self,
        person_id: str,
        image_bytes: bytes,
        filename: str = "face.jpg",
        face_box: dict | None = None,
        fallback_to_full_image: bool = True,
        source_observation_id: str | None = None,
    ) -> dict:
        person = self.repo.get_person(person_id)
        path = self.save_media("people", image_bytes, filename)
        image = self.vision.read_image(path)

        if face_box is None:
            boxes = self.vision.detect_faces(image, fallback_to_full_image)
            if not boxes:
                raise ValueError("No face detected in enrollment image.")
            face_box = boxes[0]

        embedding = self.vision.embedding(image, face_box)
        quality = self.vision.quality_score(image, face_box)
        captured_at = utc_now()
        media = self.repo.create_media_asset(
            file_path=path,
            source_kind="person_face_image",
            captured_at=captured_at,
            mime_type=guess_mime_type(path),
            sha256=sha256_bytes(image_bytes),
            metadata={"person_id": person_id},
        )
        face_image = self.repo.add_person_face_image(
            person_id=person_id,
            media_asset_id=media["id"],
            embedding_model=self.vision.embedding_model,
            embedding=embedding,
            face_box=face_box,
            quality_score=quality,
            source_observation_id=source_observation_id,
        )
        return {
            "person": person,
            "face_image": face_image,
            "face_box": face_box,
            "quality_score": quality,
            "embedding_model": self.vision.embedding_model,
        }

    def recognize_image(
        self,
        image_bytes: bytes,
        filename: str = "capture.jpg",
        threshold: float = 0.95,
        review_threshold: float = 0.70,
        max_candidates: int = 5,
        fallback_to_full_image: bool = False,
        source_kind: str = "api_upload",
        source_label: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        path = self.save_media("captures", image_bytes, filename)
        image = self.vision.read_image(path)
        captured_at = utc_now()
        media = self.repo.create_media_asset(
            file_path=path,
            source_kind=source_kind,
            captured_at=captured_at,
            mime_type=guess_mime_type(path),
            sha256=sha256_bytes(image_bytes),
            metadata=metadata or {},
        )
        capture = self.repo.create_capture(
            media_asset_id=media["id"],
            captured_at=captured_at,
            source_kind=source_kind,
            source_label=source_label,
            metadata=metadata or {},
        )

        references = self.repo.reference_embeddings()
        boxes = self.vision.detect_faces(image, fallback_to_full_image)
        faces = []
        type_counts: dict[str, int] = defaultdict(int)

        for index, face_box in enumerate(boxes):
            embedding = self.vision.embedding(image, face_box)
            quality = self.vision.quality_score(image, face_box)
            candidates = self.match_candidates(
                embedding,
                references,
                threshold=threshold,
                review_threshold=review_threshold,
                limit=max_candidates,
            )
            status = "unknown"
            if candidates:
                status = candidates[0]["decision"]

            observation = self.repo.add_face_observation(
                capture_id=capture["id"],
                face_index=index,
                face_box=face_box,
                quality_score=quality,
                embedding_model=self.vision.embedding_model,
                embedding=embedding,
                status=status,
            )

            for candidate in candidates:
                self.repo.add_recognition_candidate(
                    observation_id=observation["id"],
                    person_id=candidate["person"]["id"],
                    confidence=candidate["confidence"],
                    rank=candidate["rank"],
                    decision=candidate["decision"],
                )

            best = candidates[0] if candidates else None
            if best and best["decision"] == "matched":
                type_counts[best["person"]["person_type"]] += 1
            else:
                type_counts[status] += 1

            faces.append(
                {
                    "observation_id": observation["id"],
                    "face_index": index,
                    "face_box": face_box,
                    "quality_score": quality,
                    "status": status,
                    "best_candidate": best,
                    "candidates": candidates,
                }
            )

        return {
            "capture_id": capture["id"],
            "media_asset_id": media["id"],
            "face_count": len(faces),
            "summary": {
                "matched_students": type_counts.get("student", 0),
                "matched_teachers": type_counts.get("teacher", 0),
                "matched_staff": type_counts.get("staff", 0),
                "uncertain": type_counts.get("uncertain", 0),
                "unknown": type_counts.get("unknown", 0),
            },
            "threshold": threshold,
            "review_threshold": review_threshold,
            "faces": faces,
        }

    def assign_observation(
        self,
        observation_id: str,
        person_id: str,
        notes: str | None = None,
        add_to_face_profile: bool = True,
    ) -> dict:
        info = self.repo.get_observation_media(observation_id)
        feedback = self.repo.add_feedback(
            observation_id=observation_id,
            action="assign",
            person_id=person_id,
            notes=notes,
        )
        face_image = None
        if add_to_face_profile:
            source_path = Path(info["file_path"])
            image = self.vision.read_image(source_path)
            crop = self.vision.crop(image, info["face_box"])
            encoded = cv2.imencode(".jpg", crop)[1].tobytes()
            face_image = self.enroll_face(
                person_id=person_id,
                image_bytes=encoded,
                filename=f"{observation_id}.jpg",
                face_box=None,
                fallback_to_full_image=True,
                source_observation_id=observation_id,
            )
        return {
            "feedback": feedback,
            "face_image": face_image,
        }

    def stats(self) -> dict:
        return self.repo.stats()

    def save_media(self, bucket: str, image_bytes: bytes, filename: str) -> Path:
        bucket_dir = self.media_dir / bucket
        bucket_dir.mkdir(parents=True, exist_ok=True)
        path = bucket_dir / f"{new_id(bucket[:-1] or 'media')}{safe_extension(filename)}"
        path.write_bytes(image_bytes)
        return path

    def match_candidates(
        self,
        embedding: list[float],
        references: list[dict],
        threshold: float,
        review_threshold: float,
        limit: int,
    ) -> list[dict]:
        best_by_person: dict[str, dict] = {}
        for ref in references:
            confidence = self.vision.similarity(embedding, ref["embedding"])
            person_id = ref["person"]["id"]
            existing = best_by_person.get(person_id)
            if existing is None or confidence > existing["confidence"]:
                best_by_person[person_id] = {
                    "person": ref["person"],
                    "confidence": confidence,
                    "reference_face_image_id": ref["face_image_id"],
                }

        ranked = sorted(
            best_by_person.values(),
            key=lambda item: item["confidence"],
            reverse=True,
        )[:limit]

        candidates = []
        for index, item in enumerate(ranked, start=1):
            confidence = item["confidence"]
            if index == 1 and confidence >= threshold:
                decision = "matched"
            elif confidence >= review_threshold:
                decision = "uncertain"
            else:
                decision = "low_confidence"
            candidates.append(
                {
                    "rank": index,
                    "person": item["person"],
                    "confidence": confidence,
                    "decision": decision,
                    "reference_face_image_id": item["reference_face_image_id"],
                }
            )

        return [c for c in candidates if c["decision"] != "low_confidence"]

