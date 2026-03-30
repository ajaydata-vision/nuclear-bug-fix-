# Verification

## Before Fix

DLQ full with reject-publish overflow -> dead-letter attempts rejected -> main queue backing up -> publishers rejected

## After Fix

DLQ consumer drains backlog -> dead-lettering succeeds again -> normal flow resumes

## Regression Checks

Add DLQ depth metric and alert at 80% capacity; verify DLQ consumer is running in all environments
