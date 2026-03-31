# Verification

## Before Fix
order.getItems().add(item) only → order_id=NULL or duplicate insert

## After Fix
```java
// On Order entity
public void addItem(OrderItem item) {
    this.items.add(item);   // inverse side
    item.setOrder(this);    // owner side — sets FK
}

// In service
order.addItem(item);  // always use convenience method
orderRepo.save(order);
```
order_items table: order_id correctly set to order.id, no duplicates

## Regression Checks
- Single item: one row in order_items with correct order_id
- Multiple items: each row has correct order_id
- SQL log: single INSERT per item, no redundant UPDATE
