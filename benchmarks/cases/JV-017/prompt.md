# JV-017: @Async Email Method Blocks HTTP Request Thread — Responds In 4 Seconds

## User Prompt

We annotated our email notification method with `@Async` so it would run in the
background and let the HTTP response return immediately. Instead the HTTP request
still blocks for 3-4 seconds while the email sends. The endpoint takes as long
as it did before we added `@Async`. No errors. The annotation appears to be
doing nothing. What is wrong?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.3
- versions: spring-boot-starter-mail 3.2.3
- environment: development and production, same behavior
- logs:
  ```
  [INFO]  OrderController    - [ORDER] created order ORD-8821, sending confirmation
  [INFO]  EmailService       - [EMAIL] thread=http-nio-8080-exec-5 sending to customer@example.com
  [INFO]  EmailService       - [EMAIL] sent successfully (3847ms)
  [INFO]  OrderController    - [ORDER] response returned
  ```
- code excerpt:
```java
// EmailService.java
@Service
public class EmailService {

    @Async
    public void sendOrderConfirmation(String to, String orderId) {
        log.info("[EMAIL] thread={} sending to {}",
                 Thread.currentThread().getName(), to);
        // ... SMTP send takes 3-4 seconds
        log.info("[EMAIL] sent successfully ({}ms)", elapsed);
    }
}

// OrderController.java
@RestController
public class OrderController {

    private final OrderService orderService;
    private final EmailService emailService;

    @PostMapping("/orders")
    public ResponseEntity<Order> createOrder(@RequestBody OrderRequest req) {
        Order order = orderService.create(req);
        log.info("[ORDER] created order {}, sending confirmation", order.getId());
        emailService.sendOrderConfirmation(req.getEmail(), order.getId());
        log.info("[ORDER] response returned");
        return ResponseEntity.ok(order);
    }
}

// AppConfig.java
@Configuration
public class AppConfig {
    // no @EnableAsync present
}
```
- reproduction:
  1. POST /orders with valid request body
  2. Response takes 3-4 seconds (same as before @Async was added)
  3. Log shows `thread=http-nio-8080-exec-5` — HTTP executor thread, not async pool
  4. "[ORDER] response returned" appears AFTER "[EMAIL] sent successfully"
