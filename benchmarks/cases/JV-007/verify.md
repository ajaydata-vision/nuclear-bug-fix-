# Verification

## Before Fix
Client disconnect → CancelledKeyException on next selector iteration

## After Fix
```java
Iterator<SelectionKey> iter = selector.selectedKeys().iterator();
while (iter.hasNext()) {
    SelectionKey key = iter.next();
    iter.remove();  // remove BEFORE processing
    if (!key.isValid()) continue;
    if (key.isReadable()) { ... }
}
```
Client disconnect → clean key removal → no CancelledKeyException

## Regression Checks
- 100 rapid client connect/disconnect cycles: zero exceptions
- Normal read/write under load: all events processed correctly
- Concurrent disconnects: each key removed exactly once
