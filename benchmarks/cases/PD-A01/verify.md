# Verify

## before_fix

- Launch with a stored session
- Observe spinner remains forever
- No `restore_session completed` log appears

## after_fix

- Startup and `restore_session()` log the same event-loop ID
- Stored session restores and spinner clears
- Manual login still works

## regression_checks

- App exits cleanly without pending-task warnings
- Startup tasks still work on repeated launches
- No second event loop is created during startup
