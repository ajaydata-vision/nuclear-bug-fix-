# Evaluator

## Metadata

- id: JV-002
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: jsp, session-scope, request-scope, jstl, el, scope

## Ground Truth

- root_cause: Search results and query are stored in session scope (HttpSession) instead of request scope (HttpServletRequest attributes). Session scope persists for the user's entire session lifetime. When User B visits the search page without performing a search, the JSP reads from sessionScope which still has User A's data.
- why_it_happens: HttpSession is per-user but persists across requests. Data stored with session.setAttribute() survives until the session expires or the attribute is explicitly removed. Request attributes (request.setAttribute()) only live for the duration of one request-response cycle. Search results are per-request data, not per-session data.
- accepted_fix: Store results in request scope: replace session.setAttribute("searchResults", results) with req.setAttribute("searchResults", results). Update JSP to use ${requestScope.searchResults} or just ${searchResults} (EL searches request scope first).
- rejected_fix_patterns:
  - clear session attributes at start of every request (works but wasteful and error-prone)
  - store results in application scope (makes the bug worse — all users share results)

## Evidence Signals

- strongest_signal: session.setAttribute() used for per-request data (searchResults, searchQuery); JSP reads from sessionScope; User B sees User A's data only on first visit (before their own search populates the session)
- strongest_alternative_explanation: Servlet instance variable storing results (shared across all users)
- why_alternative_is_wrong: The code shows session.setAttribute() — data is per-user (User B doesn't see User C's data) but persists across requests for the same user, which is the session scope characteristic

## Scoring Notes

- full_credit_conditions:
  - identifies session scope as the wrong scope for search results
  - proposes request scope (req.setAttribute / requestScope in JSP)
  - explains that session persists across requests while request scope does not
- partial_credit_conditions:
  - identifies the wrong scope but proposes clearing session on each GET request
- fail_conditions:
  - blames concurrent thread access to the session
  - blames JSTL c:forEach behavior
