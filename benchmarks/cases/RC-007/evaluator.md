# Evaluator

## Metadata

- id: RC-007
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: async-local-storage, request-context, node, continuation-local-storage, security

## Ground Truth

- root_cause: The continuation-local storage (CLS) context is not properly bound to each request's async chain, allowing context to bleed between concurrent requests.
- why_it_happens: cls-hooked requires that the async chain be started within the namespace.run() call. Using namespace.set() without namespace.run() does not properly isolate context per request.
- accepted_fix: Use namespace.run() to create an isolated context per request: namespace.run(() => { namespace.set('userId', req.user.id); next() }). Or use Node.js built-in AsyncLocalStorage instead of cls-hooked.
- rejected_fix_patterns:
  - add a request ID to logs without fixing the context isolation
  - switch to passing context explicitly via function parameters (correct but not root cause fix)

## Evidence Signals

- strongest_signal: Wrong userId in logs correlates with concurrent load; correct under single-threaded testing; CLS namespace.set() without namespace.run()
- strongest_alternative_explanation: Node.js threading causing context mix
- why_alternative_is_wrong: Node.js is single-threaded; the contamination is from the async continuation chain not threading

## Scoring Notes

- full_credit_conditions:
  - identifies namespace.set without namespace.run as the isolation failure
  - proposes namespace.run() per request or AsyncLocalStorage
  - notes this is a security issue requiring audit
- partial_credit_conditions:
  - identifies CLS as the issue but proposes switching to explicit parameter passing without explaining the root cause
- fail_conditions:
  - adds request ID logging without fixing context isolation
  - blames Node.js threading
