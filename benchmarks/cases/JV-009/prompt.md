# JV-009: Spring Boot App Hangs on Shutdown, Container Force-Kills It

## User Prompt

When we stop our Spring Boot application (SIGTERM from Kubernetes), it hangs for 90 seconds then gets force-killed. There are no active requests during shutdown. Our background worker threads appear stuck. What is preventing clean shutdown?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, ThreadPoolTaskExecutor
- environment: Kubernetes, graceful shutdown enabled
- logs (on SIGTERM):
  - INFO  o.s.b.w.e.tomcat.GracefulShutdown - Commencing graceful shutdown
  - INFO  o.s.b.w.e.tomcat.GracefulShutdown - Graceful shutdown complete
  - INFO  o.s.c.a.ConfigurableApplicationContext - Closing application context
  - (30 second pause)
  - INFO  o.s.s.c.ThreadPoolTaskExecutor - Shutting down ExecutorService
  - (60 second pause — timeout)
  - WARN  o.s.s.c.ThreadPoolTaskExecutor - Timed out while waiting for executor to terminate
- code excerpt:
```java
@Component
public class ReportWorker {
    @Async
    public void generateReport(Long reportId) {
        while (!done) {
            try {
                Report chunk = fetchNextChunk(reportId);
                processChunk(chunk);
                Thread.sleep(100);
            } catch (InterruptedException e) {
                log.warn("Worker interrupted, continuing...");
                // flag cleared, loop continues
            }
        }
    }
}
```
- reproduction:
  1. Trigger long-running report generation
  2. Send SIGTERM to JVM
  3. Spring initiates executor shutdown (shutdownNow() interrupts threads)
  4. Worker catches InterruptedException, logs warning, continues loop
  5. Executor waits 60s for termination, force-terminates
