# Verification

## Before Fix

POST /reports → 504, DB has record, retry creates duplicate

## After Fix

POST /reports → 202 with job ID, poll endpoint returns result when ready, no duplicates

## Regression Checks

Test idempotency key prevents duplicate even if client retries the initial POST
