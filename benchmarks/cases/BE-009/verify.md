# Verification

## Before Fix

1. Run two concurrent signup requests for the same email.
2. Confirm one fails on unique constraint or both attempt to insert.

## After Fix

1. Re-run the same concurrent signup race.
2. Confirm only one user is created.
3. Confirm the loser path returns a safe existing-user or conflict result without data corruption.

## Regression Checks

- Test distinct emails still create concurrently.
- Test repeated retries for the same email.
- Test under higher concurrency than the original reproduction.

