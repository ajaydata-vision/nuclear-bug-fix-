# Verify

## before_fix

- Rapid searches trigger Qt thread-affinity warnings or crashes
- Worker thread updates widgets directly

## after_fix

- Worker emits data back to the GUI thread
- UI updates happen only on the main thread
- Searches remain stable under repeated use

## regression_checks

- Background search throughput still works
- No duplicate signals fire per result set
- Shutdown does not leave background threads touching dead widgets
