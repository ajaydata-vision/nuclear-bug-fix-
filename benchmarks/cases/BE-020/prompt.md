# BE-020: Read-After-Write Inconsistency From Replica Lag

## User Prompt

Our profile update endpoint returns success, but when the app immediately reads
the profile back it sometimes shows the old value for a few seconds. Directly
checking the primary database shows the new value immediately. What is the real
bug?

## Context Provided To The Skill

- stack: Java 17 + Spring Boot 3.2.2 + PostgreSQL 16.1
- versions: primary/replica setup with read routing
- environment: production only
- logs:
  - `UPDATE users SET display_name='Ajay' WHERE id=42` succeeds on primary
  - immediate follow-up `SELECT ...` routed to replica returns old value
  - retry after 3 seconds returns new value
- code excerpt:

```java
userRepository.updateName(id, name);      // writes to primary
return profileReadService.getById(id);    // routed through read replica
```

- reproduction:
  1. Update profile name
  2. Immediately fetch profile
  3. Observe stale value intermittently
