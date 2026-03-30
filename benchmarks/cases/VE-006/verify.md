# Verification

## Before Fix

1. Complete authorization code redirect.
2. Send the token request as implemented.
3. Confirm the provider returns `405 Method Not Allowed`.

## After Fix

1. Re-run the same flow with a POST form-encoded token exchange.
2. Confirm the provider returns access token payload successfully.
3. Confirm PKCE fields remain correct.

## Regression Checks

- Test invalid code path still returns the expected provider error.
- Test token exchange with the production redirect URI.
- Confirm no credentials leak into query strings.

