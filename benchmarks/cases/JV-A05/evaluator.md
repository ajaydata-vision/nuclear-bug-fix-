# Evaluator

## Metadata

- id: JV-A05
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: hikaricp, connection-pool, jdbc, connection-leak, try-finally, resource-management

## Ground Truth

- root_cause: JDBC Connection is acquired but not closed when PaymentValidationException is thrown. The catch block for PaymentValidationException rethrows the exception before conn.close() is reached. Each validation failure permanently leaks one connection. After pool-size (10) failures, the pool is exhausted.
- why_it_happens: The finally block apparently has conn.close() only on the success path (or is missing entirely for the exception rethrow path). When PaymentValidationException is caught and rethrown, the connection is never returned to HikariCP. HikariCP waits 30s for a connection to become available, then times out.
- accepted_fix: Use try-with-resources to guarantee connection closure on all paths:
  try (Connection conn = dataSource.getConnection();
       PreparedStatement ps = conn.prepareStatement(sql)) {
      // work — conn and ps auto-closed on any exit including exceptions
  }
- rejected_fix_patterns:
  - increase HikariCP pool size (delays the problem, does not fix the leak)
  - add connection timeout configuration (masks the symptom)
  - add conn.close() only in the PaymentValidationException catch block (fragile — leaves other exception paths unprotected)

## Evidence Signals

- strongest_signal: App recovers on restart; DB shows exactly pool-size idle connections from app; exhaustion rate matches requests that throw PaymentValidationException; finally block has conn.close() but PaymentValidationException rethrow bypasses it
- strongest_alternative_explanation: PostgreSQL server closing idle connections after timeout, returning them as broken to HikariCP
- why_alternative_is_wrong: DB server is confirmed healthy; DB shows 10 active connections from the app (not closed by server); restart fixes immediately (if server-side, restart would not help as new connections would also be closed)

## Scoring Notes

- full_credit_conditions:
  - identifies connection not closed on PaymentValidationException path
  - explains that catch+rethrow before finally conn.close() causes the leak
  - proposes try-with-resources as the fix
- partial_credit_conditions:
  - identifies connection leak without explaining the specific code path (catch+rethrow)
  - suggests increasing pool size as part of fix
- fail_conditions:
  - blames PostgreSQL server connection limits
  - suggests disabling HikariCP connection timeout
  - recommends connection pool tuning without fixing the leak
