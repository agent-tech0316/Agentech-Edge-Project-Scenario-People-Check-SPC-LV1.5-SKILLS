# SA Attendance System

Local-first attendance intelligence for dance schools and other class-based studios.

The first version treats the teacher plus iPhone camera as the "robot": the human aims
the camera, the Mac does recognition, and the teacher only resolves uncertain cases.
Later versions can replace that actor with classroom cameras, monitoring systems, or
physical robots without changing the core attendance model.

## Product Promise

One photo, one class, attendance done.

The system is designed around this daily flow:

1. The teacher opens today's class on the Mac.
2. The iPhone scans a QR code and captures a group photo or short scan.
3. The Mac detects faces, matches students, and marks high-confidence attendance.
4. The teacher confirms only uncertain faces.
5. The system exports records and learns from corrections.

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
db/
  schema.sql             SQLite-first canonical schema
docs/
  architecture.md
  database-memory-skills-terminal.md
  privacy-and-consent.md
  product-roadmap.md
  pricing.md
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
sa-attendance info --db data/attendance.sqlite
```

No cloud dependency is required for the first version. Student data and face data should
stay on the school Mac by default.

## First Commercial SKU

SA Attendance System can be sold as a per-student monthly add-on:

- Starter: up to 20 students
- Studio: 21 to 100 students
- School: 100+ students

See `docs/pricing.md` for the first pricing model.

