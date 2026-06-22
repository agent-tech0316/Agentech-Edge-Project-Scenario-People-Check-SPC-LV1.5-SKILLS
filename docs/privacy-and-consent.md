# Privacy and Consent

This product handles children's biometric data, so the default must be conservative.

## Default Policy

- Keep all student and face data on the school Mac by default.
- Require guardian or school authorization before face enrollment.
- Store consent state in the database.
- Allow a student profile and face data to be deleted.
- Keep manual attendance as an alternative for students without consent.
- Log teacher confirmations and edits for auditability.

## Data Minimization

Store only what the product needs:

- Student identity and class membership
- Face embeddings and a small number of enrollment images
- Attendance observations and final records
- Teacher corrections
- Device and camera source metadata

Avoid storing long raw camera footage unless the school explicitly enables it.

## Retention

Suggested first policy:

- Keep attendance records indefinitely or according to school policy.
- Keep uploaded group photos for 30 to 90 days.
- Keep face enrollment images while the student is active and consent remains valid.
- Delete raw recognition job artifacts after they are no longer needed for review.

## Commercial Note

Privacy is not only compliance. It is a selling point.

For dance schools, "local-first face attendance" is easier to trust than a cloud-first
biometric system.

