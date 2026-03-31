# Evaluator

## Metadata

- id: JV-A04
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: hibernate, lazy-loading, jpa, spring, transactional, session, jackson

## Ground Truth

- root_cause: The Hibernate session (and therefore the @Transactional boundary) closes when getOrder() returns. Jackson serializes the Order entity in the controller — outside the transaction. When Jackson accesses order.getItems(), the lazy proxy has no open session to initialize from and throws LazyInitializationException.
- why_it_happens: @Transactional opens a Hibernate session for the duration of the annotated method. When the method returns, the transaction commits and the session closes. The Order entity returned is a detached entity. Accessing any uninitialized lazy collection on a detached entity fails.
- accepted_fix: Use a DTO: map Order to OrderDto inside the @Transactional method while the session is still open. Return OrderDto from the service, not the entity. Alternatively: use @EntityGraph or JOIN FETCH to eagerly load items within the transaction. Or: use spring.jpa.open-in-view=true (not recommended — hides the real problem and causes performance issues).
- rejected_fix_patterns:
  - change items to FetchType.EAGER (fixes the symptom but causes N+1 and loads items on every Order fetch regardless of need)
  - add @Transactional to the controller (works technically but puts transaction management in the wrong layer)
  - enable open-in-view (keeps session open until view renders — performance antipattern)

## Evidence Signals

- strongest_signal: LazyInitializationException with "no Session" during Jackson serialization in controller; service method is @Transactional but returns the raw entity; session closes when @Transactional method returns
- strongest_alternative_explanation: Hibernate session factory misconfiguration causing sessions to close prematurely
- why_alternative_is_wrong: The session is closing at exactly the right time per JPA spec — at transaction boundary. The bug is that lazy data is being accessed after the transaction boundary, not that the session closes too early.

## Scoring Notes

- full_credit_conditions:
  - identifies that session closes when @Transactional service method returns
  - identifies Jackson serializing the lazy collection outside the transaction
  - proposes DTO mapping inside the transaction OR JOIN FETCH / @EntityGraph
- partial_credit_conditions:
  - identifies lazy loading as the problem but proposes FetchType.EAGER as the fix
  - suggests open-in-view without explaining the transaction boundary issue
- fail_conditions:
  - blames Jackson configuration
  - suggests disabling lazy loading globally
  - recommends adding @Transactional to controller without explaining why this is wrong
