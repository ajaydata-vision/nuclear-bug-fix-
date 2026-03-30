# Verification

## Before Fix

Failure in processOrder → message lost, no retry

## After Fix

Failure in processOrder → nack → message requeued for retry

## Regression Checks

Test dead-letter queue receives messages after max retries exhausted
