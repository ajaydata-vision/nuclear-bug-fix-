# Verification

## Before Fix

1. Set stock to 1.
2. Run two concurrent purchases.
3. Confirm both can pass the check and oversell or conflict incorrectly.

## After Fix

1. Repeat the same concurrent last-item checkout.
2. Confirm only one purchase succeeds.
3. Confirm stock never drops below zero.

## Regression Checks

- Test higher stock counts with concurrent buyers.
- Test retry behavior on failed second purchase.
- Test inventory integrity after process restarts.

