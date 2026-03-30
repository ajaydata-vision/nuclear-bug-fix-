# Evaluator

## Metadata

- id: DE-003
- domain: general
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: dotenv, env-var, runtime, process-env, missing-load

## Ground Truth

- root_cause: dotenv.config() is called after the environment variable is first accessed, so the variable is not yet loaded when it is read.
- why_it_happens: require('dotenv').config() must be called before any code that reads process.env variables it manages. Node.js executes code synchronously in order; calling config() after use means the variable was read as undefined.
- accepted_fix: Move require('dotenv').config() to the very first line of the entry point file, before any other require or code that reads environment variables.
- rejected_fix_patterns:
  - use dotenv-safe for validation
  - hardcode the value as a fallback

## Evidence Signals

- strongest_signal: Variable in .env is undefined but OS-set variables work; dotenv.config() called after first use of the variable
- strongest_alternative_explanation: .env file not in the working directory
- why_alternative_is_wrong: Other dotenv-loaded variables would also be undefined if the file was missing; the specific variable is the only one failing, pointing to ordering

## Scoring Notes

- full_credit_conditions:
  - identifies dotenv called after variable access
  - proposes moving config() to top of entry file
  - explains synchronous execution order
- partial_credit_conditions:
  - identifies dotenv issue but suggests adding debug logging without fixing order
- fail_conditions:
  - suggests reinstalling dotenv
  - blames Node.js module caching
