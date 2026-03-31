# Verification

## Before Fix
Intermittent NPE from spurious wakeup: if guard → poll() on empty queue → null

## After Fix
```java
while (queue.isEmpty()) {           // WHILE not IF
    try { lock.wait(); }
    catch (InterruptedException e) { Thread.currentThread().interrupt(); return; }
}
Product item = queue.poll();        // guaranteed non-null
process(item);
```
Run 5 producers + 3 consumers for 24 hours under load: zero NPEs

## Regression Checks
- Normal operation: items processed in order
- Empty queue at startup: consumer waits correctly
- Producer adds item: notify() wakes consumer, while rechecks, item processed
