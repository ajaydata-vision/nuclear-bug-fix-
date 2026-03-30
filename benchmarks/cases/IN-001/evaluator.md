# Evaluator

## Metadata

- id: IN-001
- domain: integration
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: webhook, url-change, external-service, delivery, endpoint

## Ground Truth

- root_cause: The webhook endpoint URL in the Stripe dashboard still points to the old domain that no longer routes to the application.
- why_it_happens: External webhook providers store the callback URL independently. Migrating the application domain does not automatically update external webhook registrations.
- accepted_fix: Update the webhook endpoint URL in the Stripe dashboard to the new domain. Verify by sending a test webhook event.
- rejected_fix_patterns:
  - set up a redirect from old domain to new domain as permanent fix
  - re-implement the webhook handler

## Evidence Signals

- strongest_signal: Stripe dashboard shows successful delivery to old URL; new URL receives nothing
- strongest_alternative_explanation: New domain not accepting HTTPS connections
- why_alternative_is_wrong: Other HTTPS traffic to the new domain works; the issue is Stripe still configured to use the old URL

## Scoring Notes

- full_credit_conditions:
  - identifies webhook URL not updated in external service
  - proposes updating the Stripe dashboard endpoint
  - confirms with test webhook event
- partial_credit_conditions:
  - identifies wrong URL but proposes redirect instead of updating the source
- fail_conditions:
  - redeploys the application
  - blames Stripe delivery failure
