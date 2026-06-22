# Recognition Worker

The recognition worker turns media into attendance observations.

Pipeline:

```text
media asset -> face detection -> quality scoring -> embedding -> matching -> observations
```

The worker should not directly create final attendance truth unless the resolver accepts
the confidence, schedule, and enrollment constraints.

Outputs:

- `attendance_observations`
- `recognition_jobs`
- `skill_runs`
- candidate review payloads for the Mac console

