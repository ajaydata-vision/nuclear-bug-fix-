# Evaluator

## Metadata

- id: WF-003
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: webflux, reactive, spring-security, securitycontextholder, threadlocal, reactive-context

## Ground Truth

- root_cause: SecurityContextHolder uses ThreadLocal to store the security context. In Spring WebFlux, execution may happen on different threads across operators. The Reactor scheduler thread executing orderService.createOrder() has no ThreadLocal SecurityContext. Spring Security for WebFlux stores the context in Reactor's Context API, not ThreadLocal — accessed via ReactiveSecurityContextHolder.
- why_it_happens: Spring MVC is synchronous and single-threaded per request — ThreadLocal works. Spring WebFlux is asynchronous and may switch threads across operators — ThreadLocal is not propagated across thread boundaries. Spring Security WebFlux integration uses Reactor Context, which IS propagated across the reactive chain.
- accepted_fix: Replace SecurityContextHolder usage with ReactiveSecurityContextHolder:
  return ReactiveSecurityContextHolder.getContext()
      .map(ctx -> ctx.getAuthentication().getName())
      .flatMap(username -> orderRepo.save(new Order(username, dto)));
- rejected_fix_patterns:
  - set SecurityContextHolder.MODE_INHERITABLETHREADLOCAL (propagates to child threads but not across Reactor operators)
  - inject Principal as method parameter in the controller and pass it down (correct workaround, not root cause fix)

## Evidence Signals

- strongest_signal: Works in Spring MVC, fails in WebFlux; SecurityContextHolder.getContext() returns null; WebFlux uses Reactor which executes on different threads than the request arrival thread
- strongest_alternative_explanation: Spring Security filter not configured for WebFlux (using MVC SecurityFilterChain)
- why_alternative_is_wrong: The log shows "Security: Authentication set for user=alice" — the authentication succeeded and was stored in the reactive context; the problem is retrieval using the wrong API (ThreadLocal vs Reactor Context)

## Scoring Notes

- full_credit_conditions:
  - identifies ThreadLocal not propagated across Reactor operators
  - explains ReactiveSecurityContextHolder as the correct WebFlux mechanism
  - provides ReactiveSecurityContextHolder.getContext() fix
- partial_credit_conditions:
  - suggests passing Principal from controller as parameter (correct workaround but not the root cause explanation)
- fail_conditions:
  - blames Spring Security WebFlux configuration
  - suggests switching back to Spring MVC
