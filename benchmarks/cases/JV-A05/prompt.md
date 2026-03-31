# JV-A05: App Stops Serving Requests After Running for 2 Hours

## User Prompt

Our Spring Boot API works perfectly when it starts. After about 2 hours under normal load, it starts rejecting all requests with a 30-second hang then an error. Restarting the app fixes it immediately. DB server is healthy. What is happening?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, HikariCP 5.1.0, PostgreSQL 16.1
- environment: production, ~50 req/min sustained load
- logs (normal operation):
  - INFO  c.e.OrderService - Processing order 9921 for user 441
  - INFO  c.e.PaymentService - Validating payment method for user 441
  - ERROR c.e.PaymentService - Invalid payment method: card expired
  - INFO  c.e.OrderService - Order 9921 failed validation
- logs (after 2 hours, all requests):
  - WARN  c.z.h.p.HikariPool - HikariPool-1 - Connection is not available, request timed out after 30004ms.
  - ERROR c.e.OrderController - DataAccessException: Unable to acquire JDBC Connection
- code excerpt:
```java
@Service
public class PaymentService {
    @Autowired DataSource dataSource;

    public boolean validatePayment(Long userId, PaymentDto dto) {
        Connection conn = dataSource.getConnection();
        try {
            PreparedStatement ps = conn.prepareStatement(
                "SELECT * FROM payment_methods WHERE user_id = ? AND active = true");
            ps.setLong(1, userId);
            ResultSet rs = ps.executeQuery();
            boolean valid = rs.next() && !isExpired(rs);
            if (!valid) {
                throw new PaymentValidationException("Invalid payment method");
            }
            return true;
        } catch (PaymentValidationException e) {
            throw e;   // ← rethrows without closing conn
        } catch (SQLException e) {
            throw new DataAccessException(e);
        } finally {
            // conn.close() is here for the success path... somewhere
        }
    }
}
```
- reproduction:
  1. Send requests that trigger PaymentValidationException (expired card)
  2. Pool size = 10. After 10 such requests, pool exhausted.
  3. All subsequent requests hang 30s then fail
  4. DB server shows only 10 active connections — all from this app, all idle
