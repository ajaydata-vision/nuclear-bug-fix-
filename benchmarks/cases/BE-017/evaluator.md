# Evaluator

## Metadata

- id: BE-017
- domain: backend
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: logging, log-level, debug, silent-failure, winston, pino

## Ground Truth

- root_cause: Exceptions are logged at DEBUG level which is filtered out in production where the minimum log level is INFO.
- why_it_happens: Winston (and most loggers) filter messages below the configured minimum level. DEBUG < INFO means debug messages are silently dropped in production.
- accepted_fix: Change logger.debug() to logger.error() for exception logging in catch blocks.
- rejected_fix_patterns:
  - lower production log level to DEBUG permanently
  - log exceptions to a separate file at all levels

## Evidence Signals

- strongest_signal: Errors visible at DEBUG level but not at INFO; catch blocks use logger.debug for exceptions
- strongest_alternative_explanation: Logging service outage
- why_alternative_is_wrong: Other log messages at INFO level are appearing correctly; only error-level events are missing

## Scoring Notes

- full_credit_conditions:
  - identifies wrong log level for exceptions
  - proposes logger.error() in catch blocks
  - explains log level filtering
- partial_credit_conditions:
  - identifies log level issue but proposes lowering production level instead of fixing code
- fail_conditions:
  - blames logging service
  - suggests adding more try/catch blocks without fixing the level
