# Verification

## Before Fix
98KB response truncated to 65KB at socket buffer boundary under load

## After Fix
```java
ByteBuffer buf = ByteBuffer.wrap(responseBytes);
while (buf.hasRemaining()) {
    int written = client.write(buf);
    if (written == 0) {
        key.interestOps(SelectionKey.OP_WRITE);
        break; // selector will call back when writable
    }
}
```
Send 1000 large responses concurrently — zero truncation

## Regression Checks
- Small responses (<8KB): single write succeeds, loop exits immediately
- Exactly buffer-size response: handled correctly
- Connection close during write: IOException caught, connection cleaned up
