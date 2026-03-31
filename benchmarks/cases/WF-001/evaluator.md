# Evaluator

## Metadata

- id: WF-001
- domain: java-enterprise
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: true
- requires_log_access: true
- tags: webflux, reactive, blocking, reactor, nio-thread, jdbc, scheduler, thread-starvation

## Ground Truth

- root_cause: Blocking JDBC call (jdbcRepo.findById()) executes directly on Reactor's reactor-http-nio-* thread. These threads are non-blocking I/O threads with a fixed count (2×CPU). A blocking call holds the thread. With 50 concurrent requests all blocking on JDBC, all Reactor I/O threads are exhausted and no further reactive processing can occur.
- why_it_happens: Spring WebFlux runs on Netty's event loop with a small fixed-size thread pool. These threads are designed for non-blocking I/O only. Any blocking operation (JDBC, Thread.sleep, file I/O) holds the thread and prevents other requests from progressing. With enough concurrent blocking calls, all threads are occupied and the entire server appears to hang.
- accepted_fix: Wrap the blocking JDBC call in Mono.fromCallable().subscribeOn(Schedulers.boundedElastic()). boundedElastic is designed for blocking work and grows its thread pool as needed.
- rejected_fix_patterns:
  - increase Netty thread count (delays the problem, does not fix blocking on I/O threads)
  - switch to R2DBC (correct long-term fix but not the diagnosis — and requires full migration)
  - add timeout to Mono (causes timeout errors but does not fix thread starvation)

## Evidence Signals

- strongest_signal: Thread dump shows reactor-http-nio-* threads in WAITING state on JDBC monitor; single requests work; hangs at concurrency threshold matching Reactor thread count
- strongest_alternative_explanation: Database connection pool exhaustion causing JDBC calls to queue
- why_alternative_is_wrong: DB connection pool exhaustion causes HikariCP timeout after 30s — requests would fail with an error, not hang silently. Thread dump shows threads blocked on JDBC not on HikariCP pool acquisition.

## Scoring Notes

- full_credit_conditions:
  - identifies blocking JDBC call on Reactor nio thread as root cause
  - explains Reactor thread pool exhaustion mechanism
  - proposes Mono.fromCallable().subscribeOn(Schedulers.boundedElastic())
- partial_credit_conditions:
  - identifies blocking as the problem but proposes R2DBC migration without explaining the immediate fix
- fail_conditions:
  - blames DB connection pool without thread dump evidence
  - suggests increasing server memory or thread count
