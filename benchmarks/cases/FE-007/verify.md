# Verification

## Before Fix

1. Submit form
2. Confirm 422 and numeric date in request body

## After Fix

1. Submit same form
2. Confirm 200/201 and ISO string in request body

## Regression Checks

- Test timezone edge cases (UTC vs local)
- Test date at midnight boundary
