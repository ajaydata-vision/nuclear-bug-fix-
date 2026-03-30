# Verification

## Before Fix

GET /users/42/posts → all posts from all users

## After Fix

Same endpoint → only posts by user 42

## Regression Checks

Test endpoint with multiple users to confirm isolation
