# JV-018: User Profile API Returns Stale Data After Update — Cache Not Invalidated

## User Prompt

Our user profile endpoint reads from a Redis cache. When a user updates their
display name the PUT endpoint returns the new name correctly. But the GET endpoint
immediately after still returns the old name. The stale data persists until the
application restarts. The cache eviction code is there — it just does not seem to
be working. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.3, Spring Cache with Redis, spring-data-redis 3.2.3
- versions: Redis 7.2
- environment: development and production, reproducible every time
- logs:
  - After GET: `[CACHE] MISS — loading user 42 from DB`  ← first call, as expected
  - After GET again: (no log line) ← cache HIT, serves cached value
  - After PUT update: `[CACHE] evicting user 42`
  - After GET again: (no log line) ← should be a MISS, but it's a HIT returning old data
- code excerpt:
```java
@Service
public class UserService {

    @Cacheable(value = "users", key = "#userId")
    public UserProfile getUser(Long userId) {
        log.info("[CACHE] MISS — loading user {} from DB", userId);
        return userRepository.findById(userId).orElseThrow();
    }

    @CacheEvict(value = "users", key = "#user.id")
    public UserProfile updateUser(UserProfile user) {
        log.info("[CACHE] evicting user {}", user.getId());
        return userRepository.save(user);
    }
}

// UserProfile.java (JPA entity — note getId() return type)
@Entity
public class UserProfile {
    @Id
    private Integer id;      // ← Integer, not Long (common in JPA entities)
    private String displayName;

    public Integer getId() { return id; }
    // ...
}
```
- reproduction:
  1. GET /users/42 → MISS log, loads from DB, caches with key `42`
  2. GET /users/42 → no log, returns cached value
  3. PUT /users/42 with `{"id": 42, "displayName": "New Name"}` → evict log appears
  4. GET /users/42 → no MISS log — returns old cached displayName
  5. redis-cli: `KEYS users::*` shows `users::42` still present after eviction
