# Database, Memory, Skills, and Terminal Work

This document defines what belongs in each system layer.

## Database

The database stores stable business facts and audit-friendly events.

Create and maintain these tables first:

- `students`: student identity and status
- `guardians`: parent/guardian contacts and consent state
- `classes`: recurring class definitions
- `class_sessions`: a specific class occurrence
- `enrollments`: student membership in classes
- `devices`: iPhones, Mac cameras, camera systems, future robots
- `camera_sources`: RTSP/ONVIF/NVR stream definitions
- `media_assets`: photos, frames, and captured media references
- `face_profiles`: one profile per student identity
- `face_embeddings`: face vectors and quality metadata
- `recognition_jobs`: async worker jobs
- `attendance_observations`: candidate recognition events
- `attendance_records`: final attendance truth
- `teacher_confirmations`: human corrections and confirmations
- `memory_facts`: learned facts and soft knowledge
- `skill_runs`: skill execution logs
- `audit_logs`: compliance and debugging trail

## Memory System

Memory is not a replacement for the database. Memory makes the system smarter.

Use four memory families:

- Identity memory: who the student is and which face profile belongs to them.
- Scene memory: which room, time window, and camera belongs to each class.
- Correction memory: which students are often confused and how teachers corrected it.
- Behavior memory: patterns such as recurring lateness or room changes.

Storage rule:

- Hard facts go into normalized tables.
- Face vectors go into `face_embeddings` first, with a vector database later if needed.
- Teacher corrections go into `teacher_confirmations` and generate `memory_facts`.
- AI summaries and soft patterns go into `memory_facts`.

## AI Skills

Each skill should be callable from a UI, background worker, CLI, or future robot.

Initial skills:

- `CaptureSkill`: receive photo, video frame, or camera snapshot
- `FaceDetectSkill`: locate faces and estimate quality, pose, blur, and occlusion
- `FaceRecognizeSkill`: compare detected faces against known student face profiles
- `AttendanceResolveSkill`: combine recognition, schedule, enrollment, and thresholds
- `HumanConfirmSkill`: send uncertain cases to teacher review
- `ReportSkill`: export daily, weekly, and per-class attendance reports

Second phase skills:

- `CameraWatchSkill`: watch a room camera during scheduled class windows
- `FrameSelectSkill`: choose the clearest frames from a stream
- `MultiCameraMergeSkill`: merge duplicate observations across cameras
- `CorrectionLearningSkill`: learn from teacher corrections

Future robot skills:

- `RobotObserveSkill`: observe students from an embodied robot camera
- `RobotPromptStudentSkill`: ask a student or teacher for clarification
- `RobotNotifyTeacherSkill`: report unresolved attendance issues

## Terminal and Worker Tasks

These tasks should start as CLI commands or background jobs:

- Initialize local database
- Import student CSV files
- Batch import face enrollment photos
- Generate or refresh face embeddings
- Process uploaded iPhone photos
- Pull frames from RTSP streams
- Run recognition jobs
- Export CSV or Excel reports
- Backup local database and media
- Clean old media by retention policy

Teacher-facing work should go into the Mac UI. Admin and technical maintenance can
stay as CLI tools until the workflow is proven.

