# Verify

## before_fix

- Sync and UI write overlap can produce `database is locked`
- One of the updates may silently fail or lag

## after_fix

- Writes are serialized or otherwise coordinated
- No lock errors occur during overlapping sync/UI activity
- UI state reflects the committed database rows

## regression_checks

- Burst sync still completes
- UI edits still persist while sync is idle
- App shutdown does not leave the database busy
