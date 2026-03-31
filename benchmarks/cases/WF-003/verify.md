# Verification

## Before Fix
auth == null inside reactive service despite authenticated request

## After Fix
```java
return ReactiveSecurityContextHolder.getContext()
    .map(ctx -> ctx.getAuthentication().getName())
    .flatMap(username -> orderRepo.save(new Order(username, dto)));
```
Authentication name correctly available inside reactive chain

## Regression Checks
- Unauthenticated request: ReactiveSecurityContextHolder.getContext() returns empty, 401 returned
- Multiple concurrent authenticated users: each gets their own context correctly
- Nested flatMap calls: context propagates through all operator chain levels
