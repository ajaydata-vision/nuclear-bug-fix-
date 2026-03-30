# Verification

## Before Fix

process.env.DATABASE_URL → undefined

## After Fix

Move config() to top → process.env.DATABASE_URL → correct value

## Regression Checks

Confirm .env is not committed to version control
