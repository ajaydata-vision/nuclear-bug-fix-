# OR-001: Order List API Is Fast in Dev, Times Out in Production

## User Prompt

Our Spring Boot order list endpoint responds in 50ms in development. In production with 5000 orders, it times out after 30 seconds. The database query itself takes under 10ms. There are no slow query logs. What is causing the timeout?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Hibernate 6.4, PostgreSQL 16.1
- environment: production, 5000 order records with items
- logs:
  - WARN  o.h.e.j.s.SqlExceptionHelper - SQL timeout
  - (no slow query log entries — individual queries fast)
- code excerpt:
```java
@Entity
public class Order {
    @Id Long id;
    @OneToMany(mappedBy = "order")  // FetchType.LAZY by default
    private List<OrderItem> items;
}

@Service
public class OrderService {
    @Transactional(readOnly = true)
    public List<OrderDto> listOrders() {
        List<Order> orders = orderRepo.findAll();  // 1 query
        return orders.stream()
                     .map(o -> new OrderDto(o.getId(), o.getItems().size())) // N queries
                     .collect(toList());
    }
}
```
- reproduction:
  1. Enable spring.jpa.show-sql=true
  2. Call GET /orders
  3. Log shows: SELECT * FROM orders (1 query), then SELECT * FROM order_items WHERE order_id=? repeated 5000 times
