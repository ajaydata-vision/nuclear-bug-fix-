# Verification

## Before Fix
Burst of 26+ tasks: RejectedExecutionException, email task dropped, no log

## After Fix
```java
return new ThreadPoolExecutor(5, 10, 60L, TimeUnit.SECONDS,
    new ArrayBlockingQueue<>(20),
    (task, executor) -> {
        log.error("Email task rejected — queuing to DB for retry");
        fallbackQueue.save(task);
    });
```
Burst of 1000 tasks: all tasks logged, none silently dropped

## Regression Checks
- Normal load: tasks execute in pool normally
- Burst at exactly capacity: last task accepted without rejection
- Burst exceeding capacity: rejection handler fires, task persisted for retry
