# Verification

## Before Fix

All users rate-limited simultaneously (all appear as 127.0.0.1)

## After Fix

Rate limiting applies individually per real client IP

## Regression Checks

Verify trust proxy is set to the correct hop count for your proxy setup
