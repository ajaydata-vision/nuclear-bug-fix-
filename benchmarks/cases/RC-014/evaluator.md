# Evaluator

## Metadata

- id: RC-014
- domain: frontend
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react, unmount, setState, async, memory-leak, useEffect, cleanup

## Ground Truth

- root_cause: The async fetch callback closes over setUser and calls it after the component has unmounted, because there is no cleanup to cancel the fetch or ignore the result.
- why_it_happens: useEffect runs asynchronously. If the component unmounts before the Promise resolves, the .then() callback still executes and calls setState on the now-unmounted component.
- accepted_fix: Use AbortController to cancel the fetch on cleanup: const controller = new AbortController(); fetch(url, { signal: controller.signal }); return () => controller.abort(). Catch the AbortError and skip setState.
- rejected_fix_patterns:
  - add a mounted ref flag (isMounted pattern) — this is the old pattern React now discourages
  - wrap setUser in a try/catch

## Evidence Signals

- strongest_signal: Warning correlates exactly with navigating away during a pending fetch; no warning on fast connections where fetch completes before navigation
- strongest_alternative_explanation: React 18 concurrent mode bug
- why_alternative_is_wrong: This is expected React behavior — the fix is proper async cleanup, not a React bug

## Scoring Notes

- full_credit_conditions:
  - identifies missing AbortController cleanup
  - proposes AbortController with abort() in cleanup return
  - handles AbortError gracefully
- partial_credit_conditions:
  - identifies the lifecycle issue but uses deprecated isMounted ref pattern
- fail_conditions:
  - wraps setUser in try/catch without aborting the fetch
  - disables the React warning with eslint-disable
