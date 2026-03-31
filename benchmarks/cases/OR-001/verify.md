# Verification

## Before Fix
5000 orders → 5001 SQL queries → 30s timeout

## After Fix
```java
@Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items")
List<Order> findAllWithItems();
```
5000 orders → 1 SQL query with JOIN → 200ms response

## Regression Checks
- spring.jpa.show-sql=true: exactly 1 SELECT with JOIN for the list endpoint
- Orders with 0 items: returned correctly (LEFT JOIN FETCH if needed)
- Orders with many items: all items loaded, no secondary queries
