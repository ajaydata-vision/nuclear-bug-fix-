# Verification

## Before Fix
User B visiting /search without a query sees User A's results in sessionScope

## After Fix
1. Change: req.setAttribute("searchResults", results) and req.setAttribute("searchQuery", query)
2. Update JSP: ${searchResults} and ${searchQuery} (requestScope, not sessionScope)
3. User B visits /search with no query → empty results (or default page)
4. User B searches → sees only their own results

## Regression Checks
- User A searches, User B searches simultaneously — each sees own results
- Same user searches twice — second search overwrites first correctly
- Session expiry — no stale data issue after fix
