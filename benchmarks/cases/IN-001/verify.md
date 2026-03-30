# Verification

## Before Fix

Stripe event sent → old URL → not received

## After Fix

Update Stripe endpoint → new URL → event received

## Regression Checks

Audit all external services for outdated webhook URLs after domain changes
