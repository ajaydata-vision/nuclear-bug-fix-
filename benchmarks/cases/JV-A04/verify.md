# Verification

## Before Fix

1. GET /orders/1 throws 500 with LazyInitializationException
2. order.items never serialized

## After Fix (DTO approach)

1. Create OrderDto with List<OrderItemDto> items
2. Map inside @Transactional: return new OrderDto(order) while session open
3. GET /orders/1 returns 200 with full order including items array

## After Fix (JOIN FETCH approach)

1. Add @Query("SELECT o FROM Order o JOIN FETCH o.items WHERE o.id = :id")
2. GET /orders/1 returns 200 with items loaded in single SQL query

## Regression Checks

- Order with 0 items: returns empty items array (not null)
- Order with 50 items: all items serialized correctly
- Verify SQL query count with query logging: JOIN FETCH = 1 query, not N+1
- spring.jpa.open-in-view=false in properties — confirm fix works without open-in-view
