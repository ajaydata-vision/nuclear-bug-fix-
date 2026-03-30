# Verification

## Before Fix

Upload to instance A → GET sometimes hits instance B → 404

## After Fix

Upload to S3 → GET from any instance → always accessible

## Regression Checks

Test file access after instance restart and scaling events
