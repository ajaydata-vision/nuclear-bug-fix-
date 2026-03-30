# Verification

## Before Fix

POST login → 200; GET profile → 401 (no cookie sent)

## After Fix

POST login → 200; GET profile → 200 (cookie sent correctly)

## Regression Checks

Test CSRF protection still adequate with relaxed SameSite
