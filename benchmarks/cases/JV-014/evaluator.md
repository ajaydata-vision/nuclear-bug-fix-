# Evaluator

## Metadata

- id: JV-014
- domain: java-enterprise
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: spring-security, filter, filterchain, webfilter, addFilterBefore, securitycontext, jwt

## Ground Truth

- root_cause: JwtFilter is registered via @WebFilter and @Component, which registers it as a servlet filter OUTSIDE Spring Security's SecurityFilterChain. Spring Security's own filters (including SecurityContextPersistenceFilter which manages the SecurityContext lifecycle) run as a separate filter chain. After JwtFilter sets the Authentication, Spring Security's chain runs and its context management overwrites or clears the SecurityContext, losing the authentication.
- why_it_happens: Spring Security maintains its own ordered filter chain internally. Filters must be explicitly added to this chain via HttpSecurity.addFilterBefore/After/At() to participate in SecurityContext management. @WebFilter/@Component registers a filter in the standard servlet container filter chain, which is separate from Spring Security's internal chain.
- accepted_fix: Remove @WebFilter from JwtFilter. Register it via HttpSecurity in SecurityConfig: http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class). This places JwtFilter inside Spring Security's chain at the correct position.
- rejected_fix_patterns:
  - use FilterRegistrationBean to register JwtFilter (still outside Security chain)
  - move SecurityContextHolder.setAuthentication() to a later filter (does not fix chain membership)

## Evidence Signals

- strongest_signal: Filter logs show authentication set correctly; controller sees null principal; @WebFilter used instead of http.addFilterBefore(); Spring Security's chain overwrites the context
- strongest_alternative_explanation: JWT validation logic setting authentication to the wrong object type
- why_alternative_is_wrong: The debug log confirms "Authentication set for userId=441" meaning the object was successfully set; if the type were wrong, Spring Security's authorization would throw an exception rather than treating as anonymous

## Scoring Notes

- full_credit_conditions:
  - identifies @WebFilter registering filter outside Spring Security chain
  - explains that SecurityContextPersistenceFilter overwrites the externally set Authentication
  - proposes http.addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class)
- partial_credit_conditions:
  - identifies Spring Security chain as the issue but proposes @Order as fix
- fail_conditions:
  - suggests changing SecurityContextHolder strategy
  - recommends disabling Spring Security's CSRF or session management
