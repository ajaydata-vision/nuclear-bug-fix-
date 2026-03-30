# Verification

## Before Fix

1. Inject high latency into Service B.
2. Send normal traffic to Service A.
3. Confirm A workers block and upstream requests fail.

## After Fix

1. Repeat the same latency injection.
2. Confirm A fails fast or degrades gracefully instead of hanging.
3. Confirm queue backlog and upstream latency remain bounded.

## Regression Checks

- Test normal healthy downstream latency.
- Test partial downstream outage.
- Test recovery after the circuit closes again.

