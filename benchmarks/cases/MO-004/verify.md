# Verification

## Before Fix

1. Profile memory on 3GB device while scrolling
2. Confirm growing heap

## After Fix

1. Apply size constraints
2. Profile same scenario
3. Confirm stable memory

## Regression Checks

- Test image quality still acceptable at constrained sizes
- Test on high-RAM device unchanged
