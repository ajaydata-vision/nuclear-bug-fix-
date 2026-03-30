# Evaluator

## Metadata

- id: RC-011
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: session, fixation, concurrent, login, race, security

## Ground Truth

- root_cause: Concurrent login requests from the same client share a session object. Both modify req.session.userId concurrently, creating a race where one write overwrites the other.
- why_it_happens: express-session loads the session from the store at request start. Two concurrent requests load the same session and independently modify it. The last save wins, potentially with inconsistent data.
- accepted_fix: Regenerate the session on login: req.session.regenerate(() => { req.session.userId = user.id; req.session.save(cb) }). This creates a new session ID preventing fixation and concurrent modification.
- rejected_fix_patterns:
  - add a mutex per user ID around the session save
  - disable concurrent requests with rate limiting

## Evidence Signals

- strongest_signal: userId mismatch correlates with concurrent login requests; same session ID being modified by two requests
- strongest_alternative_explanation: Redis session store race condition
- why_alternative_is_wrong: The race is at the application level (Node.js reading and writing the same session object); Redis is consistent but the application-level merge is the issue

## Scoring Notes

- full_credit_conditions:
  - identifies concurrent session modification race
  - proposes session.regenerate() on login
  - notes this also prevents session fixation attacks
- partial_credit_conditions:
  - identifies the race but proposes only rate limiting concurrent logins
- fail_conditions:
  - blames Redis consistency
  - adds a sleep between session operations
