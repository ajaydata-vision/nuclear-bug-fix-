# JV-005: NIO Proxy Drops Random Bytes — Messages Arrive Corrupted

## User Prompt

Our Java NIO TCP proxy relays messages between clients and an upstream server. Under low load everything works. Under moderate load (20+ concurrent connections), messages arrive with missing bytes at random positions. No exception is thrown. What is causing the corruption?

## Context Provided To The Skill

- stack: Java 17, plain java.nio.channels.SocketChannel (non-blocking mode)
- environment: production, Linux, 20+ concurrent connections
- logs:
  - [DEBUG] Read 1024 bytes from client
  - [DEBUG] Sent 847 bytes to upstream  ← partial send, 177 bytes remaining
  - [DEBUG] Buffer cleared
  - [DEBUG] Read next chunk from client
- code excerpt:
```java
private void relay(SocketChannel from, SocketChannel to) throws IOException {
    ByteBuffer buf = ByteBuffer.allocate(4096);
    int read = from.read(buf);
    if (read > 0) {
        buf.flip();
        to.write(buf);   // may not write all bytes
        buf.clear();     // BUG: clears regardless of remaining bytes
    }
}
```
- reproduction:
  1. Send 4096-byte messages through proxy under load
  2. Under load, to.write(buf) returns less than buf.remaining()
  3. Unwritten bytes discarded by buf.clear()
  4. Next read fills buffer from position 0, overwriting the gap
