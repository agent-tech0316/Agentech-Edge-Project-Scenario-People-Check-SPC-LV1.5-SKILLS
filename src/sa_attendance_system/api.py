from __future__ import annotations

import json
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .service import SAAttendanceService
from .utils import decode_image_payload


API_ROUTES = {
    "GET /health": "Health check.",
    "GET /v1/stats": "Database object counts.",
    "GET /v1/people": "List known people.",
    "POST /v1/people": "Create a person.",
    "POST /v1/people/{person_id}/face-images": "Enroll a face image for a person.",
    "POST /v1/recognize": "Recognize faces in an uploaded image.",
    "POST /v1/observations/{observation_id}/assign": "Assign an observed face to a person.",
}


class APIError(Exception):
    def __init__(self, status: HTTPStatus, message: str):
        self.status = status
        self.message = message
        super().__init__(message)


class SAAttendanceRequestHandler(BaseHTTPRequestHandler):
    service: SAAttendanceService

    server_version = "SAAttendanceAPI/0.1"

    def do_GET(self) -> None:
        self.handle_request("GET")

    def do_POST(self) -> None:
        self.handle_request("POST")

    def log_message(self, format: str, *args: object) -> None:
        return

    def handle_request(self, method: str) -> None:
        try:
            parsed = urlparse(self.path)
            path = parsed.path.rstrip("/") or "/"

            if method == "GET" and path == "/health":
                self.send_json({"status": "ok", "service": "sa-attendance-system"})
                return

            if method == "GET" and path in {"/", "/v1"}:
                self.send_json({"name": "SA Attendance System", "routes": API_ROUTES})
                return

            if method == "GET" and path == "/v1/stats":
                self.send_json(self.service.stats())
                return

            if method == "GET" and path == "/v1/people":
                self.send_json({"people": self.service.list_people()})
                return

            if method == "POST" and path == "/v1/people":
                payload = self.read_json()
                display_name = payload.get("display_name")
                if not display_name:
                    raise APIError(HTTPStatus.BAD_REQUEST, "display_name is required.")
                person = self.service.create_person(
                    display_name=display_name,
                    person_type=payload.get("person_type", "student"),
                    external_id=payload.get("external_id"),
                    notes=payload.get("notes"),
                    metadata=payload.get("metadata"),
                )
                self.send_json({"person": person}, HTTPStatus.CREATED)
                return

            people_face_prefix = "/v1/people/"
            people_face_suffix = "/face-images"
            if (
                method == "POST"
                and path.startswith(people_face_prefix)
                and path.endswith(people_face_suffix)
            ):
                person_id = path[
                    len(people_face_prefix) : -len(people_face_suffix)
                ].strip("/")
                payload = self.read_json()
                image_bytes, filename = decode_image_payload(payload)
                result = self.service.enroll_face(
                    person_id=person_id,
                    image_bytes=image_bytes,
                    filename=filename,
                    face_box=payload.get("face_box"),
                    fallback_to_full_image=payload.get("fallback_to_full_image", True),
                )
                self.send_json(result, HTTPStatus.CREATED)
                return

            if method == "POST" and path == "/v1/recognize":
                payload = self.read_json()
                image_bytes, filename = decode_image_payload(payload)
                result = self.service.recognize_image(
                    image_bytes=image_bytes,
                    filename=filename,
                    threshold=float(payload.get("threshold", 0.95)),
                    review_threshold=float(payload.get("review_threshold", 0.70)),
                    max_candidates=int(payload.get("max_candidates", 5)),
                    fallback_to_full_image=payload.get("fallback_to_full_image", False),
                    source_kind=payload.get("source_kind", "api_upload"),
                    source_label=payload.get("source_label"),
                    metadata=payload.get("metadata"),
                )
                self.send_json(result, HTTPStatus.CREATED)
                return

            assign_prefix = "/v1/observations/"
            assign_suffix = "/assign"
            if (
                method == "POST"
                and path.startswith(assign_prefix)
                and path.endswith(assign_suffix)
            ):
                observation_id = path[len(assign_prefix) : -len(assign_suffix)].strip("/")
                payload = self.read_json()
                person_id = payload.get("person_id")
                if not person_id:
                    raise APIError(HTTPStatus.BAD_REQUEST, "person_id is required.")
                result = self.service.assign_observation(
                    observation_id=observation_id,
                    person_id=person_id,
                    notes=payload.get("notes"),
                    add_to_face_profile=payload.get("add_to_face_profile", True),
                )
                self.send_json(result, HTTPStatus.CREATED)
                return

            raise APIError(HTTPStatus.NOT_FOUND, f"Route not found: {method} {path}")

        except APIError as exc:
            self.send_json({"error": exc.message}, exc.status)
        except KeyError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self.send_json({"error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)

    def read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise APIError(HTTPStatus.BAD_REQUEST, f"Invalid JSON: {exc}") from exc

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def make_server(
    host: str,
    port: int,
    db_path: Path,
    media_dir: Path,
) -> ThreadingHTTPServer:
    service = SAAttendanceService(db_path=db_path, media_dir=media_dir)

    class Handler(SAAttendanceRequestHandler):
        pass

    Handler.service = service
    return ThreadingHTTPServer((host, port), Handler)

