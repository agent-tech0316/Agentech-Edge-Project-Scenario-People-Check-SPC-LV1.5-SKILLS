# Scenario People Check API

The first MVP is a people-check capability layer. It does not manage courses,
enrollment, tuition, or attendance workflow. Other apps can call this API and decide
what to do with the result.

## Start Server

```bash
PYTHONPATH=src python3 -m sa_attendance_system.cli serve \
  --db data/attendance.sqlite \
  --media-dir data/media \
  --host 127.0.0.1 \
  --port 8765
```

## Routes

### `GET /health`

Returns service status.

### `GET /v1/people`

Lists known people.

### `POST /v1/people`

Creates a person.

```json
{
  "display_name": "Sarah",
  "person_type": "student",
  "external_id": "school-student-001",
  "notes": "Optional"
}
```

`person_type` should be one of:

- `student`
- `teacher`
- `staff`
- `unknown`

### `POST /v1/people/{person_id}/face-images`

Adds a reference face image for a person.

```json
{
  "filename": "sarah-front.jpg",
  "image_base64": "...",
  "fallback_to_full_image": true
}
```

If face detection fails and `fallback_to_full_image` is true, the whole image is used
as one face. This is helpful for early data collection and tests. Production workflows
should prefer real face boxes from the detector.

### `POST /v1/recognize`

Recognizes people in an uploaded image.

```json
{
  "filename": "class-photo.jpg",
  "image_base64": "...",
  "threshold": 0.95,
  "review_threshold": 0.70,
  "max_candidates": 5,
  "fallback_to_full_image": false,
  "source_label": "teacher iphone"
}
```

Response shape:

```json
{
  "capture_id": "capture_xxx",
  "face_count": 18,
  "summary": {
    "matched_students": 15,
    "matched_teachers": 1,
    "matched_staff": 0,
    "uncertain": 1,
    "unknown": 1
  },
  "faces": [
    {
      "observation_id": "obs_xxx",
      "face_index": 0,
      "face_box": {"x": 10, "y": 20, "width": 80, "height": 80},
      "quality_score": 0.82,
      "status": "matched",
      "best_candidate": {
        "person": {
          "id": "person_xxx",
          "display_name": "Sarah",
          "person_type": "student"
        },
        "confidence": 0.98,
        "decision": "matched"
      }
    }
  ]
}
```

Decision meanings:

- `matched`: above the automatic threshold
- `uncertain`: good enough to show to a human
- `unknown`: no useful candidate

### `POST /v1/observations/{observation_id}/assign`

Manually assigns an observed face to a person and optionally adds that face crop to
the person's face profile.

```json
{
  "person_id": "person_xxx",
  "notes": "Teacher confirmed this face.",
  "add_to_face_profile": true
}
```

## MVP Vision Engine

The current engine is intentionally simple:

- OpenCV Haar face detection
- 64x64 grayscale local embedding
- cosine-like similarity scoring

It is good enough to prove the API and workflow, but it is not the final commercial
recognition model. The API is designed so the engine can be replaced later.
