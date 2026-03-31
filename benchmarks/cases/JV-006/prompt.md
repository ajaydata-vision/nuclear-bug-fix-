# JV-006: NIO Server Truncates Large Responses Under Load

## User Prompt

Our NIO HTTP server sends complete responses for small payloads. For large responses (>64KB) under load, clients receive truncated data. The server logs show no error and reports the write as successful. What is wrong?

## Context Provided To The Skill

- stack: Java 17, plain java.nio.channels.SocketChannel (non-blocking mode)
- environment: production, Linux, high-load conditions
- logs:
  - [INFO] Preparing response: 98304 bytes
  - [INFO] Write call returned: 65536 bytes
  - [INFO] Response sent successfully ← logged after single write call
- code excerpt:
```java
private void sendResponse(SocketChannel client, byte[] responseBytes) throws IOException {
    ByteBuffer buf = ByteBuffer.wrap(responseBytes);
    int written = client.write(buf);
    log.info("Write call returned: {} bytes", written);
    log.info("Response sent successfully");
}
```
- reproduction:
  1. Client requests large resource (98KB JSON payload)
  2. Server writes to non-blocking SocketChannel
  3. write() returns 65536 — socket send buffer was full
  4. Remaining 32768 bytes silently not sent
  5. Client receives truncated JSON, parse fails
