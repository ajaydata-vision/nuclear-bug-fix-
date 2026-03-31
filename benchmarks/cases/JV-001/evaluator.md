# Evaluator

## Metadata

- id: JV-001
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: servlet, filter, web.xml, annotation, ordering, tomcat, security

## Ground Truth

- root_cause: Mixing @WebFilter annotation with web.xml filter declarations causes unspecified ordering. When web.xml declares CorsFilter explicitly, Tomcat processes web.xml-declared filters before @WebFilter-annotated filters in its implementation. More critically, the Servlet 3.x specification does not define ordering between @WebFilter annotations — making the ordering of AuthFilter relative to CorsFilter undefined and deployment-dependent.
- why_it_happens: The Servlet specification does not guarantee ordering of @WebFilter annotations across classes. When CorsFilter is declared in web.xml and AuthFilter uses @WebFilter, Tomcat's actual execution order is implementation-defined. In this case CorsFilter runs first and its chain.doFilter() passes through without triggering AuthFilter properly due to filter chain construction order.
- accepted_fix: Remove @WebFilter from AuthFilter and declare it explicitly in web.xml before CorsFilter. Explicit web.xml ordering is the only guaranteed ordering mechanism in plain Servlet.
- rejected_fix_patterns:
  - add @Order annotation to @WebFilter (not supported by Servlet spec — Spring-only)
  - change @WebFilter url-pattern (does not fix ordering)
  - add AuthFilter to web.xml after CorsFilter (wrong order — auth must run before CORS passthrough)

## Evidence Signals

- strongest_signal: AuthFilter log line never appears for bypassed requests; CorsFilter log appears correctly; AuthFilter uses @WebFilter while CorsFilter uses web.xml declaration
- strongest_alternative_explanation: AuthFilter url-pattern does not match the request paths
- why_alternative_is_wrong: @WebFilter("/*") matches all paths; the unit test confirms the filter logic works — the issue is that the filter is not being invoked in the Tomcat chain at all for those requests

## Scoring Notes

- full_credit_conditions:
  - identifies @WebFilter vs web.xml ordering conflict as root cause
  - states that Servlet spec does not guarantee @WebFilter ordering
  - proposes declaring AuthFilter in web.xml before CorsFilter
- partial_credit_conditions:
  - identifies filter ordering as the problem but suggests @Order (wrong — Spring-only)
  - identifies the issue but recommends programmatic filter registration without explaining why
- fail_conditions:
  - blames CorsFilter implementation as intercepting requests
  - suggests changing session attribute name
