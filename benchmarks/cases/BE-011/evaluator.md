# Evaluator

## Metadata

- id: BE-011
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: cron, timezone, utc, node-cron, scheduled-job

## Ground Truth

- root_cause: The cron expression is interpreted in the server's local timezone (IST) rather than UTC, causing the job to run at the wrong UTC time.
- why_it_happens: node-cron by default uses the process timezone. Production servers often have a different timezone than development machines, causing schedule drift.
- accepted_fix: Specify timezone explicitly in the cron options: cron.schedule('0 21 * * *', fn, { timezone: 'UTC' })
- rejected_fix_patterns:
  - adjust cron expression for the server timezone offset
  - change the server timezone to UTC without making the code timezone-explicit

## Evidence Signals

- strongest_signal: Cron fires at correct local time but wrong UTC time; server timezone differs from expected
- strongest_alternative_explanation: DST change shifted the schedule
- why_alternative_is_wrong: The offset is constant (IST is always UTC+5:30, no DST); the issue is the base timezone assumption

## Scoring Notes

- full_credit_conditions:
  - identifies timezone mismatch between dev and production
  - proposes explicit timezone in cron options
  - notes that relying on server timezone is fragile
- partial_credit_conditions:
  - identifies timezone issue but proposes adjusting the cron expression instead of making it explicit
- fail_conditions:
  - suggests changing server timezone without fixing code
  - blames node-cron bug
