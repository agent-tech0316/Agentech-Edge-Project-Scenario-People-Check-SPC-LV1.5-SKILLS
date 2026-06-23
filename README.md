# Agentech Edge Project - Scenario People Check (SPC) - LV1.5 SKILLS

Local-first people-check and face recognition API for edge scenarios such as dance
schools, course photos, classroom snapshots, camera frames, and workflow apps.

The first MVP is intentionally smaller than a full attendance app: it is a Scenario
People Check API. Given a photo, it detects faces, matches known students/teachers/staff,
counts unknown faces, and returns JSON for another workflow app to use.

## Product Promise

One photo in, recognized people out.

The first API is designed around this flow:

1. Create people: student, teacher, staff, or unknown.
2. Enroll face images for known people.
3. Upload a photo from an iPhone, camera, monitor screenshot, or another app.
4. Receive face count, matched people, uncertain people, and unknown people.
5. Assign uncertain/unknown faces later so the system learns.

## Architecture Shape

```text
apps/
  mac-console/           Mac local command center
  iphone-capture/        iPhone browser capture surface
services/
  recognition-worker/    Face detection, embedding, matching jobs
  camera-watch/          Future RTSP/ONVIF/NVR camera ingestion
packages/
  core/                  Shared domain model, agent contracts, skill interfaces
src/
  sa_attendance_system/  Early Python CLI and local database bootstrap
tests/
  test_face_api_service.py
db/
  schema.sql             SQLite-first canonical schema
docs/
  architecture.md
  api.md
  database-memory-skills-terminal.md
  decisions.md
  privacy-and-consent.md
  product-roadmap.md
  pricing.md
  sdk.md
logs/
  project-log.md          Running project ledger
config/
  school.example.toml
data/
  local runtime data, ignored by git
```

## Core Abstractions

- Actor: teacher, iPhone, camera, monitor system, or future robot.
- Sensor: photo upload, video frame, camera stream, manual input.
- Observation: what the system saw before it becomes a final attendance decision.
- Attendance record: the final business truth for a class session.
- Memory: durable facts and learned patterns that improve future decisions.
- Skill: replaceable capability such as capture, face recognition, confirmation, export.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
sa-attendance init --db data/attendance.sqlite
sa-attendance serve --db data/attendance.sqlite --media-dir data/media
```

No cloud dependency is required for the first version. Student data and face data should
stay on the school Mac by default.

## SPC API Quick Test

```bash
PYTHONPATH=src python3 -m sa_attendance_system.cli create-person "Sarah" --type student
PYTHONPATH=src python3 -m sa_attendance_system.cli enroll-face person_xxx photos/sarah.jpg
PYTHONPATH=src python3 -m sa_attendance_system.cli recognize photos/class-photo.jpg
```

See `docs/api.md` and `docs/sdk.md` for HTTP and Python SDK usage.

## First Commercial SKU

Scenario People Check can be sold as a per-student or per-scenario monthly add-on:

- Starter: up to 20 students
- Studio: 21 to 100 students
- School: 100+ students

See `docs/pricing.md` for the first pricing model.
