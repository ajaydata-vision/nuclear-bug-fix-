# Verification

## Before Fix

Process crash → lock persists forever → operation permanently blocked

## After Fix

Process crash → TTL expires after 30s → lock released → next process can acquire

## Regression Checks

Verify TTL is longer than maximum expected operation duration; test crash scenario
