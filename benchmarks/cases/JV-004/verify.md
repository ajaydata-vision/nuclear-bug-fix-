# Verification

## Before Fix
${user.name} renders empty; request.getAttribute("user") is null

## After Fix
1. Add after user lookup: req.setAttribute("user", user);
2. Profile page renders: "Welcome, Alice"
3. Scriptlet: request.getAttribute("user") returns User object

## Regression Checks
- Null user (invalid session): handle gracefully before setAttribute
- Multiple user attributes: all resolve correctly via EL
