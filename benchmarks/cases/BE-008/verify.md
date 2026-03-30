# Verification

## Before Fix

Migration runs → success logged → staging updated → production unchanged

## After Fix

CI/CD migration with production URL → production updated → application works

## Regression Checks

Add database host check at migration start; never commit DATABASE_URL to .env for production-adjacent environments
