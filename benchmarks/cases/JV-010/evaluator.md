# Evaluator

## Metadata

- id: JV-010
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: thread-pool, rejected-execution, executor, abort-policy, spring-boot, background-task

## Ground Truth

- root_cause: ThreadPoolExecutor with the default AbortPolicy throws RejectedExecutionException when both the thread pool and the bounded queue are full. The execute() call site has no try/catch, so the exception propagates up. The task (email send) is silently dropped.
- why_it_happens: ThreadPoolExecutor's default rejection policy (AbortPolicy) throws RejectedExecutionException synchronously on the calling thread when the pool cannot accept a task. If the caller does not handle this exception, the task is lost. This is distinct from Executors.newFixedThreadPool() which uses an unbounded queue (tasks never rejected, but queue grows without bound).
- accepted_fix: Specify a RejectedExecutionHandler. Use CallerRunsPolicy for backpressure (submitting thread runs the task), or a custom handler that at minimum logs the rejection and queues to a persistent store (database, message queue) for retry.
- rejected_fix_patterns:
  - increase queue size (delays the problem under higher burst)
  - add try/catch that swallows RejectedExecutionException (hides the loss without fixing it)

## Evidence Signals

- strongest_signal: "Email task submitted" log appears but email never sent; no error log; ThreadPoolExecutor with bounded queue and no RejectedExecutionHandler configured; burst traffic exceeding pool+queue capacity
- strongest_alternative_explanation: sendConfirmationEmail() throwing an uncaught exception inside the task
- why_alternative_is_wrong: An exception inside the submitted Runnable would appear in the executor's uncaught exception handler or be swallowed silently — but the "Email task submitted" log would still appear for every order. The issue is that some orders show the submitted log but never produce any subsequent activity, suggesting the task was never actually submitted.

## Scoring Notes

- full_credit_conditions:
  - identifies RejectedExecutionException from AbortPolicy as root cause
  - explains that no RejectedExecutionHandler means AbortPolicy is default
  - proposes CallerRunsPolicy or custom logging handler
- partial_credit_conditions:
  - identifies task loss but recommends only increasing queue size
- fail_conditions:
  - blames Spring @Async configuration
  - suggests the email service is dropping tasks
