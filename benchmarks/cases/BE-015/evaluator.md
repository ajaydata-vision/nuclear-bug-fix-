# Evaluator

## Metadata

- id: BE-015
- domain: backend
- track: bohrbug-core
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: session-leak, shared-state, module-level, concurrent-requests, security

## Ground Truth

- root_cause: currentUser is a module-level variable shared across all requests. Concurrent requests overwrite each other's value, causing one user to receive another user's data.
- why_it_happens: Node.js modules are singletons. A module-level variable is shared across all concurrent request handlers. Async operations allow the variable to be overwritten between assignment and use.
- accepted_fix: Remove the module-level variable and use a local variable inside the handler: const currentUser = await getUser(req.session.userId)
- rejected_fix_patterns:
  - add a mutex lock around the handler
  - convert to class-based handlers

## Evidence Signals

- strongest_signal: Data leak only under concurrent load; module-level mutable variable in request handler
- strongest_alternative_explanation: Session store returning wrong session data
- why_alternative_is_wrong: The session lookup returns the correct user; the data leak happens after, when the module variable is overwritten

## Scoring Notes

- full_credit_conditions:
  - identifies shared module-level variable as the leak
  - proposes local variable scoped to handler
  - explains Node.js module singleton and async interleaving
- partial_credit_conditions:
  - identifies the variable as the issue but proposes mutex locking
- fail_conditions:
  - blames session store
  - suggests adding request ID tracking without fixing the shared state
