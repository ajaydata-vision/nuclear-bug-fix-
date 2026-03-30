# Evaluator

## Metadata

- id: DE-001
- domain: general
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: docker, rebuild, stale-container, sentinel, deploy

## Ground Truth

- root_cause: The running container image was never rebuilt from the changed source before restart.
- why_it_happens: Restarting an old container does not change the code baked into the image.
- accepted_fix: Rebuild the image and restart the container from the new build, then verify the sentinel log.
- rejected_fix_patterns:
  - change more code
  - blame application logic first
  - accept missing sentinel as normal logging variance

## Evidence Signals

- strongest_signal: The sentinel log from the edited code never appears
- strongest_alternative_explanation: Logs are going to the wrong sink
- why_alternative_is_wrong: The running container also reports the old app version, confirming stale runtime code

## Scoring Notes

- full_credit_conditions:
  - identifies stale image / no rebuild
  - proposes rebuild plus sentinel verification
  - treats missing sentinel as a deployment problem first
- partial_credit_conditions:
  - spots wrong code running but gives generic restart advice only
- fail_conditions:
  - keeps changing code without verifying runtime artifact
  - blames the business logic
