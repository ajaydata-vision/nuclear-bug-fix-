# Verification

## Before Fix

Production third-party call → ETIMEDOUT

## After Fix

Add outbound rule → call succeeds

## Regression Checks

Security review: confirm the rule is scoped to specific endpoints, not open outbound
