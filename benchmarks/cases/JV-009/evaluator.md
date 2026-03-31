# Evaluator

## Metadata

- id: JV-009
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: interrupted-exception, thread-pool, shutdown, spring-boot, async, interrupt-flag

## Ground Truth

- root_cause: The InterruptedException catch block swallows the interrupt without restoring the interrupted flag (Thread.currentThread().interrupt() not called). When Spring's executor calls shutdownNow(), it interrupts worker threads to signal them to stop. The worker catches the interrupt, logs a warning, and continues the while loop — the interrupt signal is permanently lost. The executor waits for termination and times out.
- why_it_happens: InterruptedException clears the thread's interrupted flag when caught. The thread pool shutdown mechanism relies on interruption to signal threads to exit. If a thread swallows the interrupt (doesn't restore the flag or doesn't exit), the pool cannot terminate that thread and waits until its awaitTermination timeout expires.
- accepted_fix: In the catch block, either restore the interrupted flag and exit the loop, or check the interrupted flag in the while condition:
  catch (InterruptedException e) { Thread.currentThread().interrupt(); break; }
  or: while (!done && !Thread.currentThread().isInterrupted()) { ... }
- rejected_fix_patterns:
  - increase awaitTermination timeout (delays the problem, does not fix it)
  - use daemon threads (threads killed abruptly, may corrupt state)

## Evidence Signals

- strongest_signal: "Worker interrupted, continuing..." log appears during shutdown; thread pool times out waiting for termination; InterruptedException caught without Thread.currentThread().interrupt(); loop continues after interrupt
- strongest_alternative_explanation: fetchNextChunk() hanging on a blocking network call that ignores interruption
- why_alternative_is_wrong: The log shows "Worker interrupted, continuing" meaning the InterruptedException was thrown from Thread.sleep(100), not from a blocking I/O call — sleep is interruptible and throws immediately. The worker explicitly continues the loop after the interrupt.

## Scoring Notes

- full_credit_conditions:
  - identifies swallowed InterruptedException (missing Thread.currentThread().interrupt())
  - explains that interrupt flag is cleared when InterruptedException is caught
  - proposes restoring flag + breaking the loop
- partial_credit_conditions:
  - identifies the interrupt handling as wrong but only adds interrupt() without breaking loop
- fail_conditions:
  - suggests increasing shutdown timeout
  - recommends using daemon threads
