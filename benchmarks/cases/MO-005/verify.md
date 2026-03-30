# Verification

## Before Fix

1. Go offline.
2. Create one or more local edits.
3. Reconnect the device.
4. Confirm no sync request fires until app restart.

## After Fix

1. Repeat the exact offline-edit-reconnect flow.
2. Confirm pending changes sync immediately on reconnect.
3. Confirm already-synced items are not duplicated.

## Regression Checks

- Test multiple queued items.
- Test reconnect with unstable network.
- Test app background/foreground transitions during reconnect.

