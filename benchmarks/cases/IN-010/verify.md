# Verification

## Before Fix

Client sends Authorization → Gateway strips it → Lambda gets no header → 401

## After Fix

Configure header mapping → Lambda receives Authorization → 200

## Regression Checks

Test all headers required by the backend are mapped in API Gateway
