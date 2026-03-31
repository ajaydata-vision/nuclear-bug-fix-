# Evaluator

## Metadata

- id: BI-003
- domain: bridge-adapters
- track: evidence-limited
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: false
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: ntscraper, scraper, upstream-drift, evidence-limited, provider-change

## Ground Truth

- root_cause: This is upstream/provider drift in the unofficial scraper path, not a local application parser bug. The upstream response shape changed and the scraper no longer finds the markers it expects.
- why_it_happens: Unofficial scrapers rely on unstable markup/tokens. A provider-side HTML/auth change can produce 200 responses with zero parsed results and no local code change.
- accepted_fix: Treat it as scraper/provider breakage first. Confirm via external intelligence, pin or upgrade to a fixed scraper release if available, or add fallback/error handling until the scraper is adapted. Do not rewrite local post-processing first.
- rejected_fix_patterns:
  - rewrite local ranking/business logic before checking upstream drift
  - blame the app's empty-state UI
  - assume `status=200` proves the provider contract is unchanged

## Evidence Signals

- strongest_signal: Raw response signature changed, items dropped to zero without local code change, and the maintainer issue reports the same breakage on the same day.
- strongest_alternative_explanation: The application's own parser/filter layer is dropping valid results.
- why_alternative_is_wrong: The log already shows the expected upstream marker is absent before local post-processing runs.

## Scoring Notes

- full_credit_conditions:
  - identifies this as upstream scraper/provider drift rather than local app logic
  - explicitly uses external-intelligence evidence
  - proposes provider-aware mitigation: pin/upgrade/fallback/explicit error handling
- partial_credit_conditions:
  - suspects upstream drift but does not explain why local parser code is not the first suspect
- fail_conditions:
  - rewrites local result filtering
  - blames Windows networking with no evidence
  - treats empty results as a frontend rendering issue
