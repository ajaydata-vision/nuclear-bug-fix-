# Verification

## Before Fix

1. Use Axios 0.27.1 in the browser upload flow.
2. Submit a multipart request.
3. Confirm the server rejects it with invalid boundary behavior.

## After Fix

1. Upgrade or adjust the client request so the browser sets the boundary correctly.
2. Re-run the exact same upload.
3. Confirm the server accepts the multipart payload successfully.

## Regression Checks

- Test multiple file sizes.
- Test JSON requests still behave normally.
- Confirm the chosen fix works in the target browsers, not only one browser.

