# Architecture Decisions

## 2026-06-22: Build Face API Before Course Workflow

Decision:

Build the first MVP as a standalone Face API instead of a complete attendance app.

Reason:

The valuable reusable skill is "given an image, detect faces, identify known people,
and return uncertain/unknown faces." Course, enrollment, schedule, and teacher review
can live in a separate workflow app later.

Implications:

- The API stores `people`, `person_face_images`, `captures`, `face_observations`,
  and `recognition_candidates`.
- `student`, `teacher`, and `staff` are person types, not separate identity systems.
- Course/session logic remains outside the first Face API.
- Human confirmation is represented as feedback or assignment, not final attendance.

## 2026-06-22: Keep First Runtime Dependency-Light

Decision:

Use a standard-library HTTP server and SQLite for the first API runtime.

Reason:

The school Mac should be able to run the first version locally without installing a
large web stack. The API contract matters more than framework choice at this stage.

Implications:

- The server can be replaced with FastAPI or another framework later.
- The SDK calls HTTP JSON endpoints, so external apps do not depend on internals.
- The current vision engine is replaceable.

