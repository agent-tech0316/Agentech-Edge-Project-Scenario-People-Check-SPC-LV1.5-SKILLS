# SA Attendance System Project Log

This file is the running ledger for SA Attendance System. Keep entries simple,
chronological, and factual.

## 2026-06-21

- Created the local project scaffold for SA Attendance System.
- Placed the project under the local Agentech AI project folder naming pattern as
  `G004-小工具-SA Attendance System`.
- Defined the first architecture around a local-first Mac command center, iPhone
  capture surface, recognition worker, future camera watcher, database, memory,
  and skill boundaries.
- Added the first SQLite schema with students, classes, sessions, observations,
  attendance records, face profiles, embeddings, memory facts, skill runs, and
  audit logs.
- Added a minimal Python CLI for database initialization and inspection.
- Verified that the CLI can initialize a SQLite database.
- Initialized a local Git repository and created the first commit:
  `897c3dd Initial SA Attendance System scaffold`.
- Confirmed that this project is independent from FFHacks and any hackathon repo.

## 2026-06-22

- Confirmed the project should stay focused on SA Attendance System and not pull
  in the larger Skill SDK, Mission, or Workflow framework yet.
- Confirmed that GitHub cloud setup should use a new independent repository, not
  FFHacks and not any hackathon repository.
- Removed the stale `FFHacks/SA-Attendance-System` remote from the working copy
  to prevent accidental push to the wrong namespace.
- Added this project log as the ongoing record for future development work.
- Created local commit `c11b966 Add project development log`.
- Checked cloud repository creation path. The current environment has no `gh`
  command and no `GITHUB_TOKEN` or `GH_TOKEN`, so GitHub creation is pending an
  explicit authenticated path.
- Next required decision: confirm the GitHub owner and either provide token-based
  access or approve using the logged-in browser session.
- Confirmed GitHub owner should be `AGENTECH`.
- Narrowed the MVP scope from full course attendance to a standalone Face API:
  create people, enroll face images, recognize faces in uploaded photos, count
  matched/uncertain/unknown faces, and expose everything over API/SDK.
- Added Face API database tables for people, person face images, captures, face
  observations, recognition candidates, and recognition feedback.
- Added local service layer, OpenCV-based MVP vision engine, HTTP API, Python SDK,
  CLI commands, API docs, SDK docs, architecture decisions, and a service test.
- Verified the service test passes.
- Verified Python compilation with `PYTHONPYCACHEPREFIX` pointed to `/tmp`.
- Verified the temporary localhost API on port 8876 with `GET /health`.
- Verified SDK flow: create person, enroll face, recognize image, and read stats.

## 2026-06-23

- Renamed the external project identity to `Agentech Edge Project - Scenario People
  Check (SPC) - LV1.5 SKILLS`.
- Kept the existing Python module path stable for now to reduce risk before GitHub
  cloud push.
- Confirmed target GitHub owner/account should be `agent-tech0316` / `info@agent-tech.ai`.
- Checked the intended GitHub SSH remote
  `git@github.com:agent-tech0316/Agentech-Edge-Project-Scenario-People-Check-SPC-LV1.5-SKILLS.git`.
  SSH authentication is not available on this machine yet, so cloud push is pending
  a GitHub token, GitHub CLI login, SSH key setup, or explicit browser-based repo
  creation approval.
- Verified GitHub token authentication for `agent-tech0316`.
- Confirmed the public GitHub repository exists:
  `https://github.com/agent-tech0316/Agentech-Edge-Project-Scenario-People-Check-SPC-LV1.5-SKILLS`.
- Configured `origin` with the public HTTPS repository URL without storing the token
  in git remote config.
- Split README into GitHub language-switch files: `README.md` language entry,
  `README.zh-CN.md` Chinese documentation, and `README.en.md` English documentation.
- Installed portable GitHub CLI `gh` v2.95.0 under
  `/Users/billyuanwang/Documents/Codex/tools/gh-cli/`.
- Verified `gh` is authenticated as `agent-tech0316` through the system keyring.
- Ran `gh auth setup-git` so future HTTPS git operations can use GitHub CLI
  authentication instead of manually provided tokens.
- Verified future push access with `git push --dry-run`.
