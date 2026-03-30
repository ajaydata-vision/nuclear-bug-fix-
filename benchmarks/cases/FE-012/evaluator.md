# Evaluator

## Metadata

- id: FE-012
- domain: frontend
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: spa, nginx, routing, 404, history-mode

## Ground Truth

- root_cause: Nginx tries to serve /about as a static file, which does not exist. For an SPA all routes should fall back to index.html which handles client-side routing.
- why_it_happens: SPAs use client-side routing; the server only serves one file (index.html) and JavaScript handles the URL. The Nginx config must redirect all unmatched paths to index.html instead of returning 404.
- accepted_fix: Change try_files to: try_files $uri $uri/ /index.html;
- rejected_fix_patterns:
  - serve static files for each route
  - use hash-based routing as workaround

## Evidence Signals

- strongest_signal: Nginx log shows it trying to open the route path as a file on disk
- strongest_alternative_explanation: React Router configured incorrectly
- why_alternative_is_wrong: In-app navigation works; the problem is only on direct URL access which bypasses React Router entirely

## Scoring Notes

- full_credit_conditions:
  - identifies missing fallback to index.html in Nginx
  - proposes try_files $uri $uri/ /index.html
  - explains client-side routing requires this
- partial_credit_conditions:
  - identifies server config issue but does not provide correct try_files syntax
- fail_conditions:
  - blames React Router configuration
  - suggests switching to hash routing without explaining the server fix
