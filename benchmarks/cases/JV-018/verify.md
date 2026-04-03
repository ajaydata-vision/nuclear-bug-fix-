# Verification

## Before Fix
- GET /users/42 → cached correctly
- PUT /users/42 → eviction log appears but `redis-cli KEYS users::*` shows `users::42` still present
- GET /users/42 → returns stale data (old display name)

## After Fix
Align both key expressions to use the same SpEL path:
```java
@Service
public class UserService {

    @Cacheable(value = "users", key = "#userId")
    public UserProfile getUser(Long userId) {
        log.info("[CACHE] MISS — loading user {} from DB", userId);
        return userRepository.findById(userId).orElseThrow();
    }

    // Fixed: accept userId as Long (matching @Cacheable key type) + align key expression
    @CacheEvict(value = "users", key = "#userId")
    public UserProfile updateUser(Long userId, UserProfile user) {
        log.info("[CACHE] evicting user {}", userId);
        return userRepository.save(user);
    }
}
```
Note: this changes the service method signature — update the calling controller:
```java
// UserController.java
@PutMapping("/users/{id}")
public UserProfile update(@PathVariable Long id, @RequestBody UserProfile user) {
    return userService.updateUser(id, user);  // pass id explicitly
}
```
If changing the method signature is not desirable, ensure type consistency:
```java
// Alternative: keep #user.id but ensure UserProfile.getId() returns Long (not Integer)
@CacheEvict(value = "users", key = "#user.id")
public UserProfile updateUser(UserProfile user) { ... }
// AND verify: Long UserProfile.getId() { return this.id; }
```
1. PUT /users/42 → eviction log appears
2. `redis-cli KEYS users::*` → `users::42` gone
3. GET /users/42 → MISS log appears, loads from DB, returns new display name
4. GET /users/42 again → HIT, returns new (correct) display name

## Regression Checks
- Evicting a user that was never cached: `@CacheEvict` is a no-op, no error
- Concurrent GET during evict + re-cache: Spring Cache handles this safely with Redis atomic operations
- Multiple cached users: eviction only removes the specified user's key, others unaffected
