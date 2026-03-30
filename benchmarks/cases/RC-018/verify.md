# Verification

## Before Fix

1. Start a new pod.
2. Wait until readiness turns green.
3. Send requests immediately.
4. Confirm startup requests can still fail on dependency connection errors.

## After Fix

1. Repeat the same startup flow.
2. Confirm the pod does not become ready until Redis and PostgreSQL are truly usable.
3. Confirm immediate post-readiness traffic succeeds.

## Regression Checks

- Test rolling deployments.
- Test dependency slow-start conditions.
- Confirm liveness and readiness remain distinct.

