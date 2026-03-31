# JV-A03: NIO File Server Sends Empty Responses

## User Prompt

We built a simple NIO file server in Java. The server accepts connections, reads a filename, and writes the file contents back. Client always receives 0 bytes. The server logs show the write completing without error. What is wrong?

## Context Provided To The Skill

- stack: Java 17, plain java.nio.channels (no Netty, no frameworks)
- environment: local development, single client, no load
- logs:
  - [INFO] Client connected from /127.0.0.1:54221
  - [INFO] Filename received: report.pdf
  - [INFO] File size: 48291 bytes
  - [INFO] Write returned: 0 bytes written
  - [INFO] Connection closed
- code excerpt:
```java
private void sendFile(SocketChannel client, String filename) throws IOException {
    byte[] data = Files.readAllBytes(Path.of(filename));
    ByteBuffer buffer = ByteBuffer.allocate(data.length);
    buffer.put(data);
    // buffer is now ready to send
    int written = client.write(buffer);
    log.info("Write returned: {} bytes written", written);
    client.close();
}
```
- reproduction:
  1. Start NIO server
  2. Connect client, send filename "report.pdf"
  3. Server logs confirm file read (48291 bytes)
  4. Client receives exactly 0 bytes
  5. No exception thrown on server or client
