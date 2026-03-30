# Verification

## Before Fix

Upload 3MB file → Nginx rejects → 413

## After Fix

Set client_max_body_size 50m in Nginx → upload succeeds

## Regression Checks

Test uploads at exactly the new limit boundary; test that Nginx and Express limits stay in sync
