# Evaluator

## Metadata

- id: BE-014
- domain: backend
- track: deploy-env
- difficulty: easy
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: session, in-memory, multi-instance, express-session, redis

## Ground Truth

- root_cause: express-session defaults to MemoryStore which stores sessions in the process memory of each instance. Sessions do not persist across instances or process restarts.
- why_it_happens: MemoryStore stores session data in-process. When load balancer routes the next request to a different instance, that instance has no record of the session.
- accepted_fix: Configure a shared session store: session({ store: new RedisStore({ client: redisClient }), secret: 'secret' })
- rejected_fix_patterns:
  - enable sticky sessions as the only fix
  - increase session TTL

## Evidence Signals

- strongest_signal: express-session logs MemoryStore production warning; user logouts correlate with instance routing
- strongest_alternative_explanation: Session secret changed between deployments
- why_alternative_is_wrong: The secret is static; the issue is instance-local storage not signature mismatch

## Scoring Notes

- full_credit_conditions:
  - identifies MemoryStore not shared across instances
  - proposes shared Redis store
  - quotes the express-session production warning
- partial_credit_conditions:
  - identifies multi-instance issue but proposes only sticky sessions
- fail_conditions:
  - suggests disabling session expiry
  - blames load balancer
