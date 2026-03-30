# Verification

## Before Fix

Rolling deploy → two pods run migration simultaneously → schema corruption

## After Fix

Init container runs migration once → pods start after schema is ready

## Regression Checks

Test migration idempotency; verify advisory lock works across pod restarts
