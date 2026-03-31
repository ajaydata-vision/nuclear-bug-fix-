# JV-A02: Spring Service Writes to DB But Field Stays Null After Exception

## User Prompt

Our Spring Boot order service is supposed to roll back the entire order when payment fails. Payment throws a RuntimeException, but the order record is still written to the database with a null payment_id. The @Transactional annotation is definitely on the method. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, Spring Data JPA, Hibernate 6.4.1, PostgreSQL 16.1
- versions: spring-tx 6.1.2
- environment: production, single-node deployment
- logs:
  - INFO  OrderService - Creating order for user 441
  - INFO  OrderService - Saving order record orderId=8812
  - ERROR PaymentService - Payment gateway timeout for orderId=8812
  - INFO  OrderService - processOrder completed
  - (no rollback log, no transaction log)
- code excerpt:
```java
@Service
public class OrderService {

    @Transactional
    public Order processOrder(Long userId, CartDto cart) {
        Order order = new Order(userId);
        orderRepo.save(order);           // saves order, orderId=8812 generated
        applyPayment(order, cart);       // calls method on same bean
        return order;
    }

    @Transactional(rollbackFor = Exception.class)
    private void applyPayment(Order order, CartDto cart) {
        String paymentId = paymentGateway.charge(cart.total());  // throws RuntimeException
        order.setPaymentId(paymentId);
        orderRepo.save(order);
    }
}
```
- reproduction:
  1. Submit order that triggers payment gateway timeout
  2. Expect: full rollback, no order record persisted
  3. Actual: order record in DB with payment_id = null
  4. Confirmed: @Transactional is on both methods
  5. Already tried: adding @Transactional(rollbackFor = Exception.class) to applyPayment — no effect
