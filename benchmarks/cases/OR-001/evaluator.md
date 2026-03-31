# Evaluator

## Metadata

- id: OR-001
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: hibernate, jpa, n-plus-one, lazy-loading, join-fetch, entity-graph, performance

## Ground Truth

- root_cause: N+1 query problem. findAll() executes 1 SELECT for orders. For each of the 5000 orders, accessing o.getItems() triggers a separate SELECT for that order's items. Total: 5001 queries. Individual queries are fast (sub-millisecond) but 5001 queries accumulate to 30+ seconds.
- why_it_happens: @OneToMany defaults to FetchType.LAZY. Lazy collections are proxies that load on first access. Inside the stream().map() loop, o.getItems().size() accesses the proxy for each order, triggering a database round-trip per order. This is invisible in dev with 10 records (10ms total) but catastrophic with 5000 (5000 × 6ms = 30s).
- accepted_fix: Use JOIN FETCH or @EntityGraph to load orders and items in a single query:
  @Query("SELECT DISTINCT o FROM Order o JOIN FETCH o.items")
  List<Order> findAllWithItems();
- rejected_fix_patterns:
  - change to FetchType.EAGER globally (loads items on every Order query regardless of need — causes problems elsewhere)
  - add @BatchSize(size=100) to items (reduces to 50 batched queries, better but not optimal)

## Evidence Signals

- strongest_signal: spring.jpa.show-sql shows SELECT * FROM order_items WHERE order_id=? repeated N times; timeout only with large data; individual queries fast; o.getItems() access inside stream loop
- strongest_alternative_explanation: PostgreSQL query plan choosing sequential scan on order_items (missing index)
- why_alternative_is_wrong: Slow query log shows no slow queries — each individual query is fast. The problem is query COUNT (5001 queries), not query speed. A missing index would show slow individual queries.

## Scoring Notes

- full_credit_conditions:
  - identifies N+1 query pattern as root cause
  - connects o.getItems().size() inside loop to lazy load trigger
  - proposes JOIN FETCH or @EntityGraph
- partial_credit_conditions:
  - identifies lazy loading as problem but proposes FetchType.EAGER globally
- fail_conditions:
  - blames PostgreSQL query planner
  - suggests adding database indexes
