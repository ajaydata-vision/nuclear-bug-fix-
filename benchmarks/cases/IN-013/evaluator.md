# Evaluator

## Metadata

- id: IN-013
- domain: integration
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: cicd, github-actions, branch, environment, production-deploy, missing-guard

## Ground Truth

- root_cause: The deploy job has no branch condition, so it runs on every push to any branch.
- why_it_happens: GitHub Actions workflows run on all matching push events unless a branch filter is specified. Without an if condition on the deploy job, feature branch pushes trigger production deployments.
- accepted_fix: Add branch condition: if: github.ref == 'refs/heads/main' to the deploy job, or restrict the workflow trigger: on: push: branches: [main]
- rejected_fix_patterns:
  - add manual approval to every deploy without fixing the branch condition
  - delete the workflow and recreate

## Evidence Signals

- strongest_signal: CI log shows deploy triggered from a feature branch; no if condition in deploy job
- strongest_alternative_explanation: Incorrect branch naming in workflow trigger
- why_alternative_is_wrong: The workflow trigger accepts all pushes by design; the missing guard is on the deploy job specifically

## Scoring Notes

- full_credit_conditions:
  - identifies missing branch condition on deploy job
  - proposes if: github.ref or branch filter in on.push
  - explains all-branch trigger behavior
- partial_credit_conditions:
  - adds branch filter to workflow trigger but does not protect against future workflow changes
- fail_conditions:
  - adds approval gate without branch protection
  - blames developer for pushing to wrong branch
