# JV-011: Producer-Consumer Processes Null Items Causing NullPointerException

## User Prompt

Our Java producer-consumer implementation using wait/notify crashes intermittently with NullPointerException when processing queue items. The NPE happens inside the consumer after poll() returns null. This only happens under load and is not reproducible deterministically.

## Context Provided To The Skill

- stack: Java 17, plain java.lang.Object wait/notify (no BlockingQueue)
- environment: production, intermittent under concurrent producers
- logs:
  - [ERROR] NullPointerException at ConsumerWorker.process(ConsumerWorker.java:28)
  - java.lang.NullPointerException: Cannot invoke "Product.getId()" because "item" is null
  -   at ConsumerWorker.process(ConsumerWorker.java:28)
  -   at ConsumerWorker.run(ConsumerWorker.java:19)
- code excerpt:
```java
public class ConsumerWorker implements Runnable {
    private final LinkedList<Product> queue;
    private final Object lock;

    public void run() {
        while (running) {
            synchronized (lock) {
                if (queue.isEmpty()) {
                    try { lock.wait(); } catch (InterruptedException e) { break; }
                }
                Product item = queue.poll();  // null if spurious wakeup
                process(item);               // NPE here
            }
        }
    }
}
```
- reproduction:
  1. Run with 5 producers and 3 consumers
  2. After several minutes, spurious wakeup causes consumer to call poll() on empty queue
  3. poll() returns null, process(null) throws NPE
