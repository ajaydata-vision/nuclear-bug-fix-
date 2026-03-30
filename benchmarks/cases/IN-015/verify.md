# Verification

## Before Fix

DLQ full → nacks rejected → main queue backing up → publishers rejected

## After Fix

DLQ consumer drains backlog → space available → normal flow resumes

## Regression Checks

Add DLQ depth metric and alert at 80% capacity; verify DLQ consumer is running in all environments
