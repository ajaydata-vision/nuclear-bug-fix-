# Verification

## Before Fix
- POST /orders blocks for 3-4 seconds
- Log: `[EMAIL] thread=http-nio-8080-exec-5` — HTTP thread, not async pool
- "[ORDER] response returned" appears after email completes

## After Fix
```java
// AppConfig.java
@Configuration
@EnableAsync   // ← add this
public class AppConfig {
}
```
1. POST /orders returns immediately (< 50ms)
2. Log: `[EMAIL] thread=task-1` — Spring's async task executor thread
3. "[ORDER] response returned" appears BEFORE "[EMAIL] sent successfully"
4. Email still delivered correctly in the background

## Regression Checks
- Email still sent on success: verify customer receives confirmation after async delay
- Exception in sendOrderConfirmation: configure `AsyncUncaughtExceptionHandler` so failures are logged — without it, exceptions from void @Async methods are silently discarded
- Multiple concurrent orders: each gets its own async task; thread pool does not exhaust under normal load (default executor is unbounded — configure a bounded TaskExecutor for production)
