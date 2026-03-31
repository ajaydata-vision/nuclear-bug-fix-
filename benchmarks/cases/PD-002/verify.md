# Verify

## before_fix

- Clicking Sync Inbox freezes the whole UI
- Spinner stops and window becomes unresponsive

## after_fix

- Sync runs while the UI remains interactive
- Status/progress updates still occur
- Inbox rows update after the worker result returns

## regression_checks

- IMAP errors still surface visibly
- Repeated syncs do not leak worker threads
- Shutdown during sync cancels cleanly
