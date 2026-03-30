# Verification

## Before Fix

gRPC service starts → HTTP probe fails → pod killed → CrashLoopBackOff

## After Fix

Switch to grpc probe → probe succeeds → pod stays healthy

## Regression Checks

Test both liveness and readiness probes after protocol fix
