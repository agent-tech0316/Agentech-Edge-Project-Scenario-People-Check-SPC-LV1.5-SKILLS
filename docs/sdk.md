# Python SDK

The SDK is a thin wrapper over the local Scenario People Check API.

## Start API

```bash
PYTHONPATH=src python3 -m sa_attendance_system.cli serve
```

## Use SDK

```python
from sa_attendance_system.sdk import SAAttendanceClient

client = SAAttendanceClient("http://127.0.0.1:8765")

person = client.create_person("Sarah", person_type="student")

client.enroll_face(
    person_id=person["id"],
    image_path="photos/sarah-front.jpg",
)

result = client.recognize(
    image_path="photos/today-class.jpg",
    threshold=0.95,
    review_threshold=0.70,
)

print(result["face_count"])
print(result["summary"])
```

## Manual Assignment

```python
client.assign_observation(
    observation_id="obs_xxx",
    person_id=person["id"],
    notes="Confirmed by teacher",
)
```

This lets the system learn from unknown or uncertain faces over time.
