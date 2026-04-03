# Evaluator

## Metadata

- id: JV-017
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: spring-boot, async, enableasync, aop, proxy, threading

## Ground Truth

- root_cause: `@EnableAsync` is absent from every `@Configuration` class in the application. Without it, Spring does not create an AOP proxy around `EmailService`. The `@Async` annotation is parsed but never acted upon — `sendOrderConfirmation()` executes on the caller's thread synchronously, exactly as if the annotation were not present.
- why_it_happens: `@Async` is implemented via Spring AOP. Spring weaves an asynchronous proxy around the target bean only when `@EnableAsync` activates the async infrastructure. Without this activation, the annotation is a no-op: Spring reads it during bean definition processing but no proxy is created. The caller invokes the method directly on the real object, not on an async-capable proxy.
- accepted_fix: Add `@EnableAsync` to any `@Configuration` class — the main `@SpringBootApplication` class is sufficient. Spring Boot does not auto-enable async processing; it requires explicit opt-in.
- rejected_fix_patterns:
  - move the @Async annotation to the interface (valid only with interface-based proxying — does not fix the missing @EnableAsync)
  - add @Async to the controller method
  - run the email send in a new Thread() manually (bypasses Spring's executor configuration)

## Evidence Signals

- strongest_signal: Log shows `thread=http-nio-8080-exec-5` (HTTP executor thread) inside `sendOrderConfirmation` — an `@Async` method running correctly would show a thread named `task-1` or similar from Spring's `SimpleAsyncTaskExecutor`; `AppConfig.java` shown in code excerpt contains no `@EnableAsync`
- strongest_alternative_explanation: `@Async` is in effect but self-invocation from within the same bean bypasses the proxy
- why_alternative_is_wrong: The call is made from `OrderController` to `EmailService` — two separate Spring beans. Self-invocation only occurs when a bean calls its own `@Async` method internally (`this.sendOrderConfirmation(...)`). Cross-bean calls go through the proxy when `@EnableAsync` is active. The missing `@EnableAsync` is confirmed by its absence in the shown `AppConfig.java`.

## Scoring Notes

- full_credit_conditions:
  - identifies missing `@EnableAsync` as root cause
  - cites the thread name in logs as proof (`http-nio-8080-exec-5` instead of async pool thread)
  - prescribes adding `@EnableAsync` to a `@Configuration` class
  - correctly distinguishes this from self-invocation (cross-bean call is not self-invocation)
- partial_credit_conditions:
  - identifies AOP proxy issue but prescribes moving the annotation to the interface rather than adding `@EnableAsync`
  - diagnoses correctly but does not explain why the thread name is the smoking gun
- fail_conditions:
  - suggests adding `@Transactional` or other AOP annotations
  - recommends running email in a manually created thread as the fix
  - blames the SMTP configuration for slowness
