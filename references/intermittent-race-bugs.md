# Intermittent & Race Condition Bug Playbook

The hardest class of bugs. Non-deterministic. Timing-dependent. Often disappear when observed.
This file gives you the exact systematic hunt — not theory, not "try locking things" — but
a step-by-step protocol that finds and kills every class of intermittent and race condition bug.

---

## THE FUNDAMENTAL TRUTH

An intermittent bug is NOT random. It only APPEARS random.
Every intermittent bug has an UNCONTROLLED VARIABLE — something that varies between
runs and determines whether the bug fires. Your entire job is to FIND THAT VARIABLE.

Once you find it → you control it → you can reproduce on demand → you debug like a Bohrbug.

```
Intermittent bug = Bohrbug + hidden uncontrolled variable
Fix the variable, and the bug becomes reproducible.
Make it reproducible, and it becomes solvable.
```

---

## PHASE A — SIGNATURE HUNTING (Find the Uncontrolled Variable)

Before any code analysis, interrogate the failure pattern.

### A.1 — Build the Failure Signature

Answer every question you can:

```
WHEN does it fail?
  □ Time of day (peak hours → load-related)
  □ Day of week / month boundary (cron-related, date calculation)
  □ After N requests / N minutes (resource leak, connection pool)
  □ After a specific user action (state accumulation)
  □ On first run vs subsequent runs (init race, cache state)
  □ During deployment / startup only (initialization race)

WHO triggers it?
  □ Specific user only (user-specific state, session contamination)
  □ Concurrent users (multi-user race window)
  □ Admin vs regular users (permission check timing)

WHAT input triggers it?
  □ Large payloads vs small (timeout window)
  □ Specific data values (edge case in shared state)
  □ Empty / null inputs (missing guard on shared resource)

WHERE does it fail?
  □ Only in production (load, data volume, timing)
  □ Only in CI (test ordering, parallel test execution)
  □ Only on specific machine/node (hardware speed, CPU count)
  □ Specific service or component (that component has the race)

LOAD level when it fails?
  □ Only under concurrent load (the classic race window)
  □ Only single user (timing with external service, not concurrency)
  □ Only when system is slow (resource starvation window)
```

### A.2 — The Uncontrolled Variable Shortlist

Common uncontrolled variables causing intermittent bugs:

| Variable | Symptom Pattern | Test |
|---|---|---|
| Thread scheduling order | Fails under load only | Run 100 parallel requests |
| Network latency | Fails in prod, not dev | Add artificial delay in dev |
| External service response time | Fails when service is slow | Throttle the external service |
| Clock / timer precision | Fails at specific times | Advance system clock manually |
| Memory pressure | Fails on low-memory machines | Limit process memory |
| CPU core count | Fails on multi-core only | Run on single-core VM |
| File system latency | Fails on NFS/network drives | Test on local disk vs remote |
| DB connection pool | Fails under load | Reduce pool size to 1, reproduce |
| Cache miss pattern | Fails on cold start | Clear cache, reproduce |
| Test execution order | Fails in CI, not locally | Run tests in random order |

---

## PHASE B — AMPLIFICATION (Make the Intermittent Become Consistent)

You cannot fix what you cannot reproduce. Amplify the race window until it fires every time.

### B.1 — Load Amplification
```
If the bug fails "sometimes" under load → run it with 10x the load.
Tools:
  HTTP APIs:    ab, wrk, k6, Artillery, Locust
  DB:           pgbench, sysbench
  Message Q:    produce 1000 messages simultaneously
  Threads:      spawn 100 goroutines/threads hitting the same resource
  
Target: find the load level where it fails 50%+ of the time.
That is the "critical load" — now you can bisect from there.
```

### B.2 — Artificial Delay Injection (Race Window Amplification)
The most powerful technique for making race conditions reproducible.

```
If you suspect a race window between Step A and Step B:
  Insert sleep(100ms) between A and B.
  Does the bug now fire consistently?
  YES → The race window is between A and B. Confirmed.
  NO  → Move the sleep to different location. Try again.

The sleep amplifies the race window from microseconds to milliseconds,
making the "winning" thread reliably win the race every time.

This is not a fix — it's a DIAGNOSTIC TOOL.
Remove the sleep before fixing. Fix the synchronization instead.

Example (pseudocode):
  # Suspected race between read and update
  value = read_from_db(id)      # Thread 1 reads
  time.sleep(0.1)               # ← INSERT HERE to amplify race window
  value.count += 1              # Thread 2 may have written here
  write_to_db(id, value)        # Now Thread 1 overwrites Thread 2's write

Once confirmed → remove sleep → fix with atomic operation or lock.
```

### B.3 — Loop Runs (Run Until Fail)
```
Strategy: Run the failing scenario in a tight loop until failure captured.

Shell loop:
  for i in $(seq 1 1000); do
    run_test && echo "PASS $i" || { echo "FAIL at $i"; break; }
  done

Python loop:
  for i in range(1000):
    result = run_scenario()
    if result.failed:
        print(f"FAILED at iteration {i}")
        capture_state()
        break

CI integration:
  Run flaky test in loop on dedicated "sporadic tests farm"
  under continuous recording until it fails.
  When it fails, you have the full execution trace.
```

### B.4 — Parallel Execution (Force Concurrent Access)
```
Force concurrent access to the shared resource simultaneously:

Python:
  from concurrent.futures import ThreadPoolExecutor
  with ThreadPoolExecutor(max_workers=50) as ex:
      futures = [ex.submit(the_operation) for _ in range(50)]
      results = [f.result() for f in futures]
  # Check for race: all results should be unique/correct

JavaScript:
  await Promise.all(Array(50).fill(null).map(() => theOperation()))

Java:
  ExecutorService pool = Executors.newFixedThreadPool(50);
  List<Future<?>> futures = IntStream.range(0, 50)
      .mapToObj(i -> pool.submit(theOperation))
      .collect(Collectors.toList());

If this reliably reproduces the bug → concurrent access is confirmed.
```

---

## PHASE C — NON-INVASIVE FORENSIC LOGGING

**WARNING: Standard logging causes Heisenbugs.**
Adding `print()` statements acquires I/O locks, changes thread scheduling, and makes the
race condition disappear. You are observing the system and altering the outcome.

### C.1 — Rules for Non-Invasive Logging in Race Conditions

```
NEVER use:
  □ Synchronized print/write inside the race window
  □ File I/O inside the race window
  □ Database writes inside the race window
  □ Any operation that acquires a lock inside the race window

USE instead:
  □ Lock-free data structures (atomic appends to ring buffer)
  □ Thread-local storage (each thread writes to its own buffer)
  □ Nanosecond timestamps (not milliseconds — ms is too coarse)
  □ Async logging (log to a queue, flush separately after)
  □ In-memory ring buffers (write later, after failure captured)
```

### C.2 — Operation ID Pattern (The Most Effective Race Logging)

```
Assign a unique ID to every concurrent operation. Log start and finish.
Look for interleaving of IDs in the output.

Python:
  import threading, time, uuid

  def timed_op(name, op_id):
      ts = time.perf_counter_ns()  # Nanosecond precision
      tid = threading.get_ident()
      print(f"{ts} [{op_id}] [{tid}] START {name}")
      # ... operation ...
      print(f"{time.perf_counter_ns()} [{op_id}] [{tid}] END {name} result={result}")

JavaScript:
  const {performance} = require('perf_hooks')
  const opId = crypto.randomUUID()
  const tid = worker_threads.threadId
  console.log(`${performance.now().toFixed(6)} [${opId}] [${tid}] START`)
  // ... operation ...
  console.log(`${performance.now().toFixed(6)} [${opId}] [${tid}] END`)

Reading the output:
  [op-1] [thread-A] START read      ← Thread A reads
  [op-2] [thread-B] START read      ← Thread B reads (race window opens)
  [op-2] [thread-B] END write val=1 ← Thread B writes
  [op-1] [thread-A] END write val=1 ← Thread A overwrites! (race confirmed)
  Expected value: 2. Actual: 1.
```

### C.3 — Shared State Watcher
```
Watch a shared variable without interfering:

Python (atomic read):
  # Snapshot shared state at nanosecond intervals in background thread
  import threading, time
  snapshots = []
  def watch(shared_var, interval=0.001):
      while watching:
          snapshots.append((time.perf_counter_ns(), shared_var.copy()))
          time.sleep(interval)

  watcher = threading.Thread(target=watch, args=(shared_state,), daemon=True)
  watcher.start()
  # ... run the failing scenario ...
  watching = False
  # Analyze snapshots for unexpected state transitions
```

---

## PHASE D — RACE CONDITION TYPE IDENTIFICATION

Identify the exact type. Each type has a specific fix.

### Type 1: Data Race (Read-Write or Write-Write Conflict)
```
SYMPTOM: Value wrong after concurrent writes. Counter off. Data corrupted.
MECHANISM: Thread A reads value X. Thread B reads value X.
           Both write X+1. Final value is X+1 not X+2.

PROVE IT:
  Run with Thread Sanitizer (TSan) — it WILL catch this.
  See Phase E for TSan commands per language.

FIX:
  Use atomic operations:    atomic_int, AtomicInteger, sync/atomic
  Use mutex/lock:           mutex.lock(), synchronized, @synchronized
  Use immutable + replace:  never mutate shared object, replace it atomically
  Use channels/queues:      route all writes through single writer
```

### Type 2: TOCTOU — Time-of-Check to Time-of-Use
```
SYMPTOM: Checked condition was true, but by the time of use it changed.
         "Enough inventory" checked → checked → buy → oversold
         "File exists" checked → file deleted → open fails
         "Token valid" checked → token expired → request fails

MECHANISM:
  Thread A: CHECK (passes) ──────── ACT (on now-invalid state)
                             ↑
  Thread B:           MUTATE (invalidates state A checked)

PROVE IT:
  Insert sleep between CHECK and ACT.
  Race fires consistently? → TOCTOU confirmed.

FIX:
  Atomic check-and-set:
    DB: UPDATE ... WHERE condition = expected (optimistic locking)
    Redis: SET NX (set if not exists — atomic)
    Code: Compare-and-swap (CAS) operations
  Remove the gap:
    Combine check and act into single atomic database transaction
    Use SELECT FOR UPDATE to lock row during check-and-act
    Use database constraints as the final guard (not application logic)

Example DB fix:
  WRONG:
    SELECT count FROM inventory WHERE id = ?  -- check
    if count > 0:
      UPDATE inventory SET count = count - 1  -- act (race window here)

  RIGHT:
    UPDATE inventory SET count = count - 1
    WHERE id = ? AND count > 0              -- atomic check AND act
    RETURNING count                          -- returns -1 if failed
```

### Type 3: Initialization Race (Use Before Ready)
```
SYMPTOM: NullPointerException on startup. Object used before initialized.
         Works most of the time, fails on fast machines or parallel startup.

MECHANISM: Thread A starts using object.
           Thread B is still initializing it.
           Thread A sees partially-initialized state.

PROVE IT:
  Add sleep(50ms) at the very start of the initialization.
  Does it fail more consistently? → Init race confirmed.

FIX:
  Ensure initialization completes before use:
    - Use explicit ready signals / promises / futures
    - Initialize in constructor only (no lazy init without locks)
    - Double-checked locking (must use volatile/atomic flag)
    - Use framework lifecycle hooks (Spring @PostConstruct, etc.)

Correct double-checked locking (Java):
  private volatile Singleton instance;  // ← volatile is REQUIRED
  
  public Singleton get() {
    if (instance == null) {
      synchronized(this) {
        if (instance == null) {  // check again inside lock
          instance = new Singleton();
        }
      }
    }
    return instance;
  }
```

### Type 4: Async Gap (Result Used Before Operation Completes)
```
SYMPTOM: Value is null/default even though you set it. Works when slow network/DB.
MECHANISM: Async operation started. Caller doesn't wait. Uses result before ready.

PROVE IT:
  Add artificial delay before the dependent operation.
  If it now works → async gap confirmed.

FIX:
  Await the async operation before using result.
  Use callbacks, promises, async/await, channels correctly.
  Never use result outside the continuation/callback.
```

### Type 5: Callback Timing Race
```
SYMPTOM: Event handler fires with wrong state. "This shouldn't be possible."
MECHANISM: State changes after callback is registered but before it fires.
           Callback sees stale state at registration time (closure capture).

PROVE IT:
  Log state at registration vs state inside callback. They differ.

FIX:
  Pass current state AS PARAMETER into callback — don't capture outer variable.
  Use functional update patterns: setState(prev => compute(prev))
```

### Type 6: Distributed Race (Multi-Service / Multi-Instance)
```
SYMPTOM: Data inconsistent across services. Duplicate processing. Lost updates.
MECHANISM: Service A and Service B both check "should I process this?"
           Both say yes. Both process. Duplicate.

PROVE IT:
  Check service logs across all instances simultaneously.
  Look for same request ID appearing in multiple service logs.

FIX:
  Distributed lock (Redis SETNX, Zookeeper, etcd)
  Database-level atomic operations (UPDATE ... RETURNING)
  Message queue with single consumer per partition
  Idempotency keys (detect and reject duplicate processing)
  Optimistic locking with version column:
    UPDATE records SET data=?, version=version+1
    WHERE id=? AND version=expected_version
```

### Type 7: Resource Exhaustion Race
```
SYMPTOM: Fails only under load. "Max connections", "pool exhausted", deadlock.
MECHANISM: Both threads pass the "is capacity available?" check.
           Combined they exceed capacity. One fails.

PROVE IT:
  Reduce pool/capacity to 1. Run 2 concurrent operations.
  Fails consistently? → Resource race confirmed.

FIX:
  Semaphore to limit concurrent access to resource
  Queue with bounded workers (don't let N threads race for M<N slots)
  Circuit breaker pattern (fail fast, don't queue indefinitely)
```

### Type 8: Test Ordering / Shared State Race (Flaky Tests)
```
SYMPTOM: Test passes alone, fails when run with other tests. Flaky in CI.
MECHANISM: Test B leaves state that causes Test A to fail.
           Test A assumed clean state that isn't clean.

PROVE IT:
  Run failing test in isolation. Passes?
  Run with --randomize-order flag (pytest --randomly, rspec --order random).
  Run with bisect to find minimum reproducing set (rspec --bisect).

FIX:
  Isolate test state completely (teardown, before/after each)
  Use transactions that roll back in DB tests
  Use fresh test database per test
  Mock time, random, external services
  Never share mutable state between tests
```

---

## PHASE E — RACE DETECTION TOOLS BY LANGUAGE

Use automated tools BEFORE manual diagnosis. They catch what humans miss.

### Go — Built-in Race Detector (Best in class)
```bash
# Run with race detector
go test -race ./...
go run -race main.go

# The Go race detector uses happens-before algorithm
# Zero false positives. Any report is a real race.
# 2-20x overhead — run in CI, not every dev build
# Output shows: goroutine IDs, file:line, access type (read/write)
```

### C/C++ — ThreadSanitizer (TSan)
```bash
# Compile with TSan
gcc -fsanitize=thread -g -O1 -o myapp myapp.c
clang -fsanitize=thread -g -O1 -o myapp myapp.cpp

# Run — TSan instruments memory accesses in real time
./myapp

# TSan reports: which threads, which memory locations, exact stack traces
# Memory overhead: 5-10x | CPU overhead: 2-20x
# Run on your test suite, not in production

# Also: Helgrind (via Valgrind)
valgrind --tool=helgrind ./myapp
```

### Java — Thread Sanitizer / FindBugs / JCStress
```bash
# Java Flight Recorder (built-in, low overhead)
java -XX:+UnlockCommercialFeatures -XX:+FlightRecorder \
     -XX:StartFlightRecording=duration=60s,filename=race.jfr MyApp

# JCStress — specifically for concurrency testing
# Add to pom.xml, write stress tests

# FindBugs / SpotBugs (static analysis for race patterns)
spotbugs -html report.html myapp.jar

# Also: use volatile/synchronized correctly and let the compiler warn you
```

### Python — threading + logging + loop
```python
# Python has the GIL but races still occur:
# - With asyncio (no GIL protection on async code)
# - With multiprocessing
# - With external resources (DB, files, network)

# For asyncio races — use asyncio.Lock():
lock = asyncio.Lock()
async def safe_operation():
    async with lock:
        await do_the_thing()
```

### JavaScript/Node.js — async race detector
```javascript
// Node.js async races — no threading but event loop races
// Use async_hooks to trace async context switching

const async_hooks = require('async_hooks')
// Track which async context each operation runs in

// For test flakiness — jest --runInBand (single thread)
// For async races — use fake timers to control timing
jest.useFakeTimers()
jest.runAllTimers()
```

### Databases — Lock analysis
```sql
-- PostgreSQL: find lock waits
SELECT pid, pg_blocking_pids(pid), query, state, wait_event_type, wait_event
FROM pg_stat_activity WHERE wait_event IS NOT NULL;

-- MySQL: find deadlocks
SHOW ENGINE INNODB STATUS;

-- Find race in application:
-- Add row-level locking with SELECT FOR UPDATE
-- Use explicit transaction isolation levels
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
```

---

## PHASE F — THE FIX LADDER

Apply fixes in this order — least to most invasive.

```
Level 1 — Atomic Operations (no lock, lowest overhead)
  Use when: single variable, simple increment/compare/swap
  Python:   threading.Lock() on single value, or multiprocessing.Value
  Go:       sync/atomic package
  Java:     AtomicInteger, AtomicReference, volatile
  C/C++:    std::atomic<T>
  JS:       SharedArrayBuffer + Atomics (for workers)

Level 2 — Mutex / Lock (simple critical section)
  Use when: small block of code accessing shared resource
  Python:   threading.Lock(), threading.RLock()
  Go:       sync.Mutex, sync.RWMutex
  Java:     synchronized block, ReentrantLock
  C/C++:    std::mutex, std::lock_guard
  JS:       No native mutex — use async lock libraries

Level 3 — Database Atomic Operations (for shared DB state)
  Use when: race is in the database layer
  Pattern:  UPDATE ... WHERE condition AND version = expected RETURNING *
  Pattern:  INSERT ... ON CONFLICT DO UPDATE (upsert)
  Pattern:  SELECT FOR UPDATE (explicit row lock)

Level 4 — Message Queue / Channel (serialize access)
  Use when: multiple producers/consumers, order matters
  Pattern:  All writes go through single queue, single consumer processes
  Go:       channels (built-in, idiomatic)
  Python:   queue.Queue, asyncio.Queue
  Distributed: Redis streams, Kafka, RabbitMQ

Level 5 — Distributed Lock (for multi-instance/service races)
  Use when: multiple service instances compete for same resource
  Redis:    SET key value NX PX 30000 (atomic set if not exists with TTL)
  Pattern:  Acquire lock → do work → release lock
  Critical: Lock MUST expire (TTL) so crashes don't deadlock forever

Level 6 — Redesign (eliminate shared mutable state)
  Use when: none of the above work cleanly
  Pattern:  Event sourcing (append-only, no mutation)
  Pattern:  Actor model (each actor owns its state, no sharing)
  Pattern:  Immutable data (replace instead of mutate)
  This is the most work but produces the most resilient design.
```

---

## PHASE G — VERIFICATION (Proving the Fix Held)

A fix is not a fix until proven under the same conditions that caused the failure.

```
Step 1: Reproduce the original failure (before applying fix)
  Run Phase B amplification until it fails consistently.
  Capture the failure signature.

Step 2: Apply the fix (one change only — see Rule 12)

Step 3: Re-run Phase B amplification with fix applied
  Same load. Same artificial delays. Same parallel execution.
  Must NOT fail. Run 1000+ iterations.

Step 4: Stress verification
  10x the load that originally triggered it.
  24-hour soak test if the bug was production-only.
  Run ThreadSanitizer / race detector again.

Step 5: Add a permanent regression test
  Write a test that deliberately triggers the race window.
  This test must fail without the fix and pass with it.
  Add to CI so it NEVER regresses.

  Example regression test structure:
    - Spawn N threads/goroutines targeting the shared resource
    - Run them concurrently without artificial synchronization
    - Assert the final state is correct
    - This test proves the fix, not just the absence of symptoms
```

---

## QUICK REFERENCE — INTERMITTENT BUG DECISION TREE

```
Bug fails intermittently?
│
├── Fails more often under LOAD?
│   → Concurrent access race. Phase D: Type 1 (Data Race) or Type 6 (Distributed).
│   → Use Phase B.4 (parallel execution) to amplify.
│   → Use Phase E (TSan/race detector) to confirm.
│
├── Fails only at STARTUP or INITIALIZATION?
│   → Phase D: Type 3 (Init Race).
│   → Use Phase B.2: sleep at start of init.
│
├── Fails only when EXTERNAL SERVICE is slow?
│   → Phase D: Type 4 (Async Gap).
│   → Use Phase B.2: add artificial delay before consuming result.
│
├── Fails in CI but not locally?
│   → Phase D: Type 8 (Test Ordering Race).
│   → Use Phase B.3: run with --randomize-order, then --bisect.
│
├── Fails at SPECIFIC TIME of day / month boundary?
│   → Clock/timer issue. Check cron, timezone, DST, date arithmetic.
│   → Manually advance system clock to boundary and reproduce.
│
├── Fails only on SPECIFIC DATA?
│   → TOCTOU race with specific trigger condition.
│   → Phase D: Type 2 (TOCTOU).
│   → Use Phase B.2: sleep between check and act.
│
└── Fails RANDOMLY with no pattern?
    → Phase A: Build the failure signature first.
    → The pattern IS there. You haven't found the uncontrolled variable yet.
    → Run Phase A.2 — try each variable systematically.
```
