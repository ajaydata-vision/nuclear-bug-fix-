# Verification

## Before Fix
Concurrent updates → ObjectOptimisticLockingFailureException for second writer

## After Fix (retry)
```java
@Retryable(value = ObjectOptimisticLockingFailureException.class, maxAttempts = 3,
           backoff = @Backoff(delay = 100))
@Transactional
public Order updateOrder(Long id, String newStatus) { ... }
```
Concurrent updates → second writer retries → both updates eventually succeed

## After Fix (conflict surfacing)
Return 409 Conflict to client: let user decide to refresh and retry

## Regression Checks
- Single user: no retry needed, first attempt succeeds
- 3+ concurrent conflicting users: retry resolves within maxAttempts
- Persistent conflict: after maxAttempts, exception propagates → 409 to client
