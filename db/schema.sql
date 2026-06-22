PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS students (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  legal_name TEXT,
  birth_date TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS guardians (
  id TEXT PRIMARY KEY,
  display_name TEXT NOT NULL,
  phone TEXT,
  email TEXT,
  consent_status TEXT NOT NULL DEFAULT 'unknown',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_guardians (
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  guardian_id TEXT NOT NULL REFERENCES guardians(id) ON DELETE CASCADE,
  relationship TEXT,
  PRIMARY KEY (student_id, guardian_id)
);

CREATE TABLE IF NOT EXISTS classes (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  room_name TEXT,
  level_name TEXT,
  default_start_time TEXT,
  default_duration_minutes INTEGER,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enrollments (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'active',
  joined_at TEXT,
  left_at TEXT,
  UNIQUE (student_id, class_id)
);

CREATE TABLE IF NOT EXISTS class_sessions (
  id TEXT PRIMARY KEY,
  class_id TEXT NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
  session_date TEXT NOT NULL,
  starts_at TEXT NOT NULL,
  ends_at TEXT,
  room_name TEXT,
  status TEXT NOT NULL DEFAULT 'scheduled',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS devices (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  device_type TEXT NOT NULL,
  actor_type TEXT NOT NULL,
  connection_kind TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  config_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS camera_sources (
  id TEXT PRIMARY KEY,
  device_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  room_name TEXT,
  source_kind TEXT NOT NULL,
  stream_url TEXT,
  auth_ref TEXT,
  status TEXT NOT NULL DEFAULT 'planned',
  config_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS media_assets (
  id TEXT PRIMARY KEY,
  source_kind TEXT NOT NULL,
  source_id TEXT,
  file_path TEXT NOT NULL,
  mime_type TEXT,
  captured_at TEXT NOT NULL,
  sha256 TEXT,
  metadata_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS face_profiles (
  id TEXT PRIMARY KEY,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'active',
  consent_basis TEXT NOT NULL DEFAULT 'guardian_consent',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS face_embeddings (
  id TEXT PRIMARY KEY,
  face_profile_id TEXT NOT NULL REFERENCES face_profiles(id) ON DELETE CASCADE,
  media_asset_id TEXT REFERENCES media_assets(id) ON DELETE SET NULL,
  embedding_model TEXT NOT NULL,
  embedding_json TEXT NOT NULL,
  face_box_json TEXT,
  quality_score REAL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS recognition_jobs (
  id TEXT PRIMARY KEY,
  media_asset_id TEXT REFERENCES media_assets(id) ON DELETE SET NULL,
  job_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'queued',
  started_at TEXT,
  finished_at TEXT,
  error_message TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_observations (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES class_sessions(id) ON DELETE CASCADE,
  recognition_job_id TEXT REFERENCES recognition_jobs(id) ON DELETE SET NULL,
  media_asset_id TEXT REFERENCES media_assets(id) ON DELETE SET NULL,
  source_actor_id TEXT REFERENCES devices(id) ON DELETE SET NULL,
  observed_at TEXT NOT NULL,
  candidate_student_id TEXT REFERENCES students(id) ON DELETE SET NULL,
  confidence REAL,
  face_box_json TEXT,
  quality_score REAL,
  observation_status TEXT NOT NULL DEFAULT 'candidate',
  raw_result_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance_records (
  id TEXT PRIMARY KEY,
  session_id TEXT NOT NULL REFERENCES class_sessions(id) ON DELETE CASCADE,
  student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
  status TEXT NOT NULL,
  arrived_at TEXT,
  source_kind TEXT NOT NULL,
  confidence REAL,
  resolved_by TEXT NOT NULL DEFAULT 'system',
  observation_id TEXT REFERENCES attendance_observations(id) ON DELETE SET NULL,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE (session_id, student_id)
);

CREATE TABLE IF NOT EXISTS teacher_confirmations (
  id TEXT PRIMARY KEY,
  observation_id TEXT REFERENCES attendance_observations(id) ON DELETE SET NULL,
  attendance_record_id TEXT REFERENCES attendance_records(id) ON DELETE SET NULL,
  teacher_name TEXT,
  action TEXT NOT NULL,
  previous_student_id TEXT REFERENCES students(id) ON DELETE SET NULL,
  confirmed_student_id TEXT REFERENCES students(id) ON DELETE SET NULL,
  reason TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS memory_facts (
  id TEXT PRIMARY KEY,
  memory_type TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  subject_id TEXT,
  fact_text TEXT NOT NULL,
  confidence REAL NOT NULL DEFAULT 1.0,
  source_kind TEXT NOT NULL,
  source_id TEXT,
  valid_from TEXT,
  valid_until TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS skill_runs (
  id TEXT PRIMARY KEY,
  skill_name TEXT NOT NULL,
  input_ref TEXT,
  output_ref TEXT,
  status TEXT NOT NULL,
  started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  finished_at TEXT,
  error_message TEXT,
  metrics_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS audit_logs (
  id TEXT PRIMARY KEY,
  actor_id TEXT,
  actor_type TEXT NOT NULL,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id TEXT,
  details_json TEXT NOT NULL DEFAULT '{}',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_sessions_class_date
  ON class_sessions(class_id, session_date);

CREATE INDEX IF NOT EXISTS idx_observations_session_candidate
  ON attendance_observations(session_id, candidate_student_id);

CREATE INDEX IF NOT EXISTS idx_records_session_student
  ON attendance_records(session_id, student_id);

CREATE INDEX IF NOT EXISTS idx_memory_subject
  ON memory_facts(subject_type, subject_id, memory_type);

