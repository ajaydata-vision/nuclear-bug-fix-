# Verification

## Before Fix

ETL with null categories → 15% row loss, no errors

## After Fix

Explicit null handling → all rows processed or explicitly routed

## Regression Checks

Add row count assertion comparing source to destination with tolerance logging
