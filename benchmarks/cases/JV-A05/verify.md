# Verification

## Before Fix

1. Enable HikariCP leak detection: spring.datasource.hikari.leak-detection-threshold=2000
2. Submit 10 requests with expired payment cards
3. Log shows: WARN HikariPool-1 - Connection leak detection triggered for connection...
4. 11th request hangs 30s then fails

## After Fix

1. Wrap with try-with-resources
2. Submit 100 requests with expired payment cards
3. No leak detection warnings
4. Pool never exhausts — connections returned after each request
5. DB shows connection count stays at maximum active, returns to 0 between bursts

## Regression Checks

- Valid payment: processes correctly, connection released
- SQLException: connection released via try-with-resources
- PaymentValidationException: connection released via try-with-resources
- Concurrent 50 expired card requests: pool never exhausted
