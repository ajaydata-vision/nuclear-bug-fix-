# Verification

## Finding the Second Caller

```bash
grep -rn "send_welcome_email" lib/
# Expected: finds 2+ call sites
# One in the LiveView (correctly guarded) — keep
# One in another module (controller/context/job) — remove or deduplicate
```

## After Removing Duplicate

- Production: exactly one welcome email per registration
- Tests: continue to pass (LiveView fix is correct and should stay)

## Note on Test Coverage Gap

LiveView tests cannot detect double-mount side effects from disconnected mounts.
For side effects that must run exactly once per user lifecycle (emails, audit logs),
test them via the context/service layer with explicit guards, not through LiveView tests alone.
