# OR-003: Saving Order With Items Creates Duplicate Rows in order_items Table

## User Prompt

When we save an Order with a list of OrderItems, we get duplicate rows in the order_items table or a unique constraint violation. This happens on every save. No concurrent users involved. What is wrong with our JPA mapping?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Hibernate 6.4, PostgreSQL 16.1
- environment: local and production, fully reproducible
- logs:
  - ERROR o.h.e.j.s.SqlExceptionHelper - duplicate key value violates unique constraint "order_items_pkey"
  - or: 2 rows inserted into order_items for a single OrderItem
- code excerpt:
```java
@Entity
public class Order {
    @Id @GeneratedValue Long id;
    @OneToMany(mappedBy = "order", cascade = CascadeType.ALL)
    private List<OrderItem> items = new ArrayList<>();
}

@Entity
public class OrderItem {
    @Id @GeneratedValue Long id;
    @ManyToOne
    @JoinColumn(name = "order_id")
    private Order order;   // owner side — controls FK
    private String sku;
}

// Service
Order order = new Order();
OrderItem item = new OrderItem();
item.setSku("SKU-001");
order.getItems().add(item);   // inverse side only — order FK NOT set on item
orderRepo.save(order);        // Hibernate sees inconsistency
```
- reproduction:
  1. Create Order, add OrderItem to order.items list
  2. Save order with cascade
  3. DB shows order_id = NULL in order_items, or duplicate INSERT attempts
