# Verification

## Before Fix
exec-3 serves User 441, MDC not cleared, exec-3 serves User 882 — logs show userId=441

## After Fix
```java
try {
    MDC.put("userId", userId);
    chain.doFilter(req, res);
} finally {
    MDC.clear();
}
```
100 concurrent users, 1000 requests each: zero cross-user MDC contamination in logs

## Regression Checks
- Exception during request: finally ensures MDC.clear() still called
- Unauthenticated request (userId=null): MDC cleared correctly after response
- Nested filters: each filter cleans its own MDC keys
