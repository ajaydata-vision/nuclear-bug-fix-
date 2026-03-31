# JV-010: Background Tasks Silently Disappear Under Burst Traffic

## User Prompt

Our Spring Boot API submits email sending tasks to a thread pool. Under normal load, all emails send. During traffic bursts (Black Friday style), some emails are never sent and there is no error in the logs. No exception is thrown at the call site. What is happening to the tasks?

## Context Provided To The Skill

- stack: Java 17, Spring Boot 3.2.1, java.util.concurrent.ThreadPoolExecutor
- environment: production, burst traffic ~500 req/sec
- logs (normal): [INFO] Email task submitted for order 8821
- logs (burst): [INFO] Email task submitted for order 9341  ← then nothing, email never sent
- code excerpt:
```java
@Configuration
public class ExecutorConfig {
    @Bean
    public Executor emailExecutor() {
        return new ThreadPoolExecutor(
            5, 10, 60L, TimeUnit.SECONDS,
            new ArrayBlockingQueue<>(20)
            // no RejectedExecutionHandler specified — defaults to AbortPolicy
        );
    }
}

@Service
public class OrderService {
    @Autowired Executor emailExecutor;

    public void processOrder(Order order) {
        saveOrder(order);
        emailExecutor.execute(() -> sendConfirmationEmail(order));
        // no try/catch around execute()
    }
}
```
- reproduction:
  1. Burst: 200 concurrent orders (5 threads busy, 20 queue full = 25 total)
  2. 201st task: AbortPolicy throws RejectedExecutionException
  3. Exception propagates up processOrder() call stack uncaught
  4. Email task silently lost
