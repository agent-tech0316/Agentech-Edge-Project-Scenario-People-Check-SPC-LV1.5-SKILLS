from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .utils import encode_file_base64


class SAAttendanceClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8765"):
        self.base_url = base_url.rstrip("/")

    def health(self) -> dict:
        return self.get("/health")

    def stats(self) -> dict:
        return self.get("/v1/stats")

    def list_people(self) -> list[dict]:
        return self.get("/v1/people")["people"]

    def create_person(
        self,
        display_name: str,
        person_type: str = "student",
        external_id: str | None = None,
        notes: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        return self.post(
            "/v1/people",
            {
                "display_name": display_name,
                "person_type": person_type,
                "external_id": external_id,
                "notes": notes,
                "metadata": metadata or {},
            },
        )["person"]

    def enroll_face(
        self,
        person_id: str,
        image_path: str | Path,
        fallback_to_full_image: bool = True,
        face_box: dict | None = None,
    ) -> dict:
        path = Path(image_path)
        return self.post(
            f"/v1/people/{person_id}/face-images",
            {
                "filename": path.name,
                "image_base64": encode_file_base64(path),
                "fallback_to_full_image": fallback_to_full_image,
                "face_box": face_box,
            },
        )

    def recognize(
        self,
        image_path: str | Path,
        threshold: float = 0.95,
        review_threshold: float = 0.70,
        max_candidates: int = 5,
        fallback_to_full_image: bool = False,
        source_label: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        path = Path(image_path)
        return self.post(
            "/v1/recognize",
            {
                "filename": path.name,
                "image_base64": encode_file_base64(path),
                "threshold": threshold,
                "review_threshold": review_threshold,
                "max_candidates": max_candidates,
                "fallback_to_full_image": fallback_to_full_image,
                "source_label": source_label,
                "metadata": metadata or {},
            },
        )

    def assign_observation(
        self,
        observation_id: str,
        person_id: str,
        notes: str | None = None,
        add_to_face_profile: bool = True,
    ) -> dict:
        return self.post(
            f"/v1/observations/{observation_id}/assign",
            {
                "person_id": person_id,
                "notes": notes,
                "add_to_face_profile": add_to_face_profile,
            },
        )

    def get(self, path: str) -> dict:
        with urlopen(self.base_url + path) as response:
            return json.loads(response.read().decode("utf-8"))

    def post(self, path: str, payload: dict[str, Any]) -> dict:
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            self.base_url + path,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8")
            raise RuntimeError(f"SA Attendance API error {exc.code}: {detail}") from exc

