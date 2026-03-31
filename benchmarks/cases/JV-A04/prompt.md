# JV-A04: Hibernate Blows Up Loading Order Items Outside Controller

## User Prompt

Our Spring Boot REST API throws a LazyInitializationException when the order response is being serialized. The Order entity loads fine. The orderItems collection crashes Jackson during JSON serialization. This only happens in the REST layer, not in our service tests.

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Hibernate 6.4.1, PostgreSQL 16.1, Jackson 2.16
- environment: production and local (reproducible)
- logs:
  - ERROR c.e.OrderController - Failed to serialize order response
  - org.hibernate.LazyInitializationException: could not initialize proxy [com.example.OrderItem#items] - no Session
  -   at org.hibernate.proxy.AbstractLazyInitializer.initialize(AbstractLazyInitializer.java:173)
  -   at com.fasterxml.jackson.databind.ser.BeanSerializer.serialize(BeanSerializer.java:178)
  -   at com.example.OrderController.getOrder(OrderController.java:34)
- code excerpt:
```java
// Entity
@Entity
public class Order {
    @Id Long id;
    @OneToMany(mappedBy = "order", fetch = FetchType.LAZY)
    private List<OrderItem> items;  // lazy by default
}

// Service
@Service
public class OrderService {
    @Transactional(readOnly = true)
    public Order getOrder(Long id) {
        return orderRepo.findById(id).orElseThrow();
    }
}

// Controller
@RestController
public class OrderController {
    @GetMapping("/orders/{id}")
    public ResponseEntity<Order> getOrder(@PathVariable Long id) {
        Order order = orderService.getOrder(id);
        return ResponseEntity.ok(order);  // Jackson serializes here — session already closed
    }
}
```
- reproduction:
  1. GET /orders/1
  2. Service returns Order entity successfully
  3. Jackson tries to serialize order.items during response building
  4. Hibernate session already closed — LazyInitializationException
