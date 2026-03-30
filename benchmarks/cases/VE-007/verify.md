# Verification

## Before Fix

findByIdAndUpdate with null → field retains old value

## After Fix

Use explicit $set: { field: null } → field set to null correctly

## Regression Checks

Audit all findByIdAndUpdate calls that set fields to null
