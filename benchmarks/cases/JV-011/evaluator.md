# Evaluator

## Metadata

- id: JV-011
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: wait-notify, spurious-wakeup, synchronized, producer-consumer, threading

## Ground Truth

- root_cause: The wait() call is guarded by if (queue.isEmpty()) instead of while (queue.isEmpty()). The JVM specification explicitly permits spurious wakeups — wait() can return without notify() being called. An if guard is checked once; after a spurious wakeup the consumer proceeds to poll() on an empty queue, which returns null, causing the NPE.
- why_it_happens: Java Memory Model explicitly states (JLS 17.2): "A thread can also wake up without being notified, interrupted, or timing out, a so-called spurious wakeup." The idiomatic guard for Object.wait() is always a while loop that rechecks the condition after every wakeup.
- accepted_fix: Change if (queue.isEmpty()) to while (queue.isEmpty()). The while loop rechecks the condition after every wakeup (including spurious ones) and only proceeds when the queue is actually non-empty.
- rejected_fix_patterns:
  - null check before process(item): treats the symptom, not the cause; consumer still wastes a wake cycle
  - switch to BlockingQueue.take(): correct alternative that handles spurious wakeups internally, but changes the locking model

## Evidence Signals

- strongest_signal: NPE from poll() returning null; if guard before wait(); intermittent under concurrent load (spurious wakeup frequency increases with contention)
- strongest_alternative_explanation: Producer removing item from queue between consumer's wait() return and poll() call (TOCTOU race)
- why_alternative_is_wrong: All operations (wait, poll, process) are inside synchronized(lock) block. Producer also uses synchronized(lock) to add and notify. No other thread can remove from queue while consumer holds the lock — TOCTOU is impossible here.

## Scoring Notes

- full_credit_conditions:
  - identifies if guard vs while guard as root cause (spurious wakeup vulnerability)
  - cites JVM specification permitting spurious wakeups
  - proposes while (queue.isEmpty()) fix
- partial_credit_conditions:
  - adds null check as the fix without explaining spurious wakeup
  - suggests BlockingQueue without explaining why while is required for Object.wait()
- fail_conditions:
  - blames concurrent modification of the queue from outside synchronized block
  - recommends ReentrantLock as fix without explaining the if vs while issue
