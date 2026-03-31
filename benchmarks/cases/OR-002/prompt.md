# OR-002: Concurrent Order Updates Throw OptimisticLockingFailureException

## User Prompt

Two users updating the same order simultaneously causes one of them to get an unexpected error: ObjectOptimisticLockingFailureException. This never happens with single users. Our Order entity has a @Version field. Is this a Hibernate bug?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Hibernate 6.4, PostgreSQL 16.1
- environment: production, concurrent users editing same order
- logs:
  - ERROR o.s.o.j.JpaObjectRetrievalFailureException: Unable to find com.example.Order with id 441
  - org.springframework.orm.ObjectOptimisticLockingFailureException: Row was updated or deleted by another transaction
  -   at com.example.OrderService.updateOrder(OrderService.java:44)
- code excerpt:
```java
@Entity
public class Order {
    @Id Long id;
    @Version Long version;  // optimistic locking enabled
    String status;
}

@Transactional
public Order updateOrder(Long id, String newStatus) {
    Order order = orderRepo.findById(id).orElseThrow();
    order.setStatus(newStatus);
    return orderRepo.save(order);
}
```
- reproduction:
  1. User A reads order (version=3), User B reads order (version=3)
  2. User A updates → version becomes 4, commit succeeds
  3. User B updates → expects version=3, finds version=4 → ObjectOptimisticLockingFailureException
