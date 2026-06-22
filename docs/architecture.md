# Architecture

SA Attendance System is an SA node for class attendance. It starts as a Mac and
iPhone product, but the internal model assumes that cameras and robots can become
the primary actors later.

## System Loop

```text
Capture -> Observe -> Recognize -> Resolve -> Confirm -> Remember -> Report
```

## Runtime Layers

```text
Interface layer
  Mac console
  iPhone capture page
  Teacher review screen
  Future robot or camera control surface

Agent layer
  TeacherAgent
  CameraAgent
  AttendanceAgent
  ReviewAgent
  ReportAgent

Skill layer
  CaptureSkill
  FaceDetectSkill
  FaceRecognizeSkill
  AttendanceResolveSkill
  HumanConfirmSkill
  ReportSkill
  CameraWatchSkill
  CorrectionLearningSkill

Memory layer
  Student identity memory
  Face memory
  Class and room memory
  Teacher correction memory
  Operational pattern memory

Database layer
  SQLite first
  Future Postgres option
  Face embedding/vector storage
  Media asset storage
  Audit logs

Runtime layer
  Local Mac server
  Recognition worker
  Camera stream worker
  Scheduler
  CLI and backup scripts
```

## Actor Abstraction

An actor is anything that can observe or decide.

Current version:

```text
Teacher + iPhone camera = semi-automatic attendance robot
```

Future version:

```text
Classroom camera + Mac worker = automatic attendance robot
Monitoring system + scheduler = passive attendance robot
Physical robot + camera + voice = embodied attendance robot
```

The product should never hard-code "teacher photo" as the only source. It should
record every input as an observation from an actor.

## Observation vs Record

This is the most important data split.

`attendance_observations` means:

> The system saw something and has a candidate interpretation.

Example: a face in an iPhone photo looks like Alice with confidence 0.84.

`attendance_records` means:

> The school has accepted this as the business truth.

Example: Alice attended Ballet Level 1 on 2026-06-21 at 16:02.

This lets the system support iPhone photos, RTSP cameras, future robots, manual
teacher edits, and audit history without rewriting the attendance model.

## Local-first Default

The first commercial version should run on the school Mac:

- SQLite database
- Local media folder
- Local face embeddings
- LAN-only iPhone upload
- Exportable CSV/Excel reports

Cloud sync can be added later, but it should not be required for basic attendance.

