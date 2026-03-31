# Evaluator

## Metadata

- id: JV-A02
- domain: java-enterprise
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: spring, transactional, self-invocation, proxy, aop, rollback

## Ground Truth

- root_cause: Spring @Transactional works via AOP proxy. When processOrder() calls applyPayment() on the same bean instance (this.applyPayment()), the call bypasses the Spring proxy entirely. The @Transactional annotation on applyPayment() is never processed — no new transaction opens, no rollback boundary is set. The exception thrown by applyPayment() propagates into processOrder()'s transaction, but by default RuntimeException does trigger rollback on the outer @Transactional — however the order was already saved before the exception, and without the inner transaction boundary the partial state is visible.
- why_it_happens: Spring proxies wrap beans at the container level. External calls go through the proxy (which intercepts @Transactional). Internal calls (this.method()) go directly to the target object instance, bypassing the proxy. No proxy interception = no transaction management = @Transactional silently ignored.
- accepted_fix: Refactor applyPayment() into a separate Spring bean so the call crosses the proxy boundary. Or inject self-reference: @Autowired private OrderService self; and call self.applyPayment(). Or use @Transactional only on processOrder() and keep applyPayment() as a plain private method inside the same transaction scope.
- rejected_fix_patterns:
  - add more @Transactional annotations to applyPayment (already tried, cannot work — self-invocation bypass is structural)
  - change rollbackFor attribute (the transaction never opens, so rollback config is irrelevant)
  - switch to @Transactional(propagation = REQUIRES_NEW) on applyPayment (still bypassed via self-invocation)

## Evidence Signals

- strongest_signal: applyPayment() is called on the same bean (this.applyPayment()); @Transactional already tried and has no effect; no rollback log appears despite exception
- strongest_alternative_explanation: Exception is caught somewhere and not propagating to the @Transactional boundary
- why_alternative_is_wrong: Logs show ERROR from payment but no catch block in the provided code; processOrder log shows completion after error suggesting exception did propagate but rollback did not trigger on the inner transaction because it never existed

## Scoring Notes

- full_credit_conditions:
  - identifies Spring AOP proxy self-invocation as root cause
  - explains that internal this.method() calls bypass the proxy
  - proposes extracting applyPayment to a separate bean OR self-injection
- partial_credit_conditions:
  - identifies @Transactional not working but attributes it to wrong propagation config
  - suggests AspectJ weaving as fix without explaining the proxy bypass cause
- fail_conditions:
  - blames database transaction isolation level
  - suggests adding @Transactional to the repository method
  - recommends upgrading Spring Boot version
