# JV-007: NIO Server Crashes With CancelledKeyException in Selector Loop

## User Prompt

Our NIO server crashes intermittently with CancelledKeyException inside the selector event loop. It happens when a client disconnects. The exception trace points to our key processing code. What is wrong?

## Context Provided To The Skill

- stack: Java 17, java.nio.channels.Selector, SocketChannel
- environment: production, any load level, happens on client disconnect
- logs:
  - java.nio.channels.CancelledKeyException
  -   at com.example.NioServer.processKeys(NioServer.java:84)
  -   at com.example.NioServer.run(NioServer.java:61)
  - [WARN] Client disconnected, key cancelled
- code excerpt:
```java
while (true) {
    selector.select();
    Set<SelectionKey> keys = selector.selectedKeys();
    for (SelectionKey key : keys) {   // iterating without remove
        if (key.isReadable()) {
            try {
                handleRead(key);
            } catch (IOException e) {
                key.cancel();
                key.channel().close();
            }
        }
    }
    // keys Set never cleared between iterations
}
```
- reproduction:
  1. Client connects, starts reading
  2. Client disconnects → IOException in handleRead → key.cancel() called
  3. Next selector.select() iteration: cancelled key still in selectedKeys set
  4. for (SelectionKey key : keys) processes the cancelled key
  5. CancelledKeyException thrown
