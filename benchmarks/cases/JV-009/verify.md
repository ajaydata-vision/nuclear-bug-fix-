# Verification

## Before Fix
SIGTERM → worker continues → executor times out after 60s → force kill

## After Fix
```java
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();  // restore flag
    log.info("Worker shutting down cleanly");
    break;
}
```
SIGTERM → interrupt delivered → worker exits loop → executor terminates in <1s

## Regression Checks
- Normal completion (done=true): exits without interrupt
- SIGTERM during fetchNextChunk: if fetchNextChunk is interruptible, interrupt propagates
- Multiple workers: all terminate cleanly on shutdown
