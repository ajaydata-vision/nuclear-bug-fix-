# Evaluator

## Metadata

- id: EL-010
- domain: elixir-phoenix
- pattern: Ecto N+1
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: ecto, n+1, preload, association, repo, performance

## Ground Truth

- root_cause: `user.posts` in the template accesses a lazy-loaded association. `Repo.all(User)` fetches users with posts as `%Ecto.Association.NotLoaded{}`. Accessing `user.posts` in the loop triggers a separate `SELECT * FROM posts WHERE user_id = $1` for each of the 800 users. 800 users = 801 queries (1 for users + 800 for posts).
- why_it_happens: Ecto does not lazy-load associations like ActiveRecord or Hibernate. Accessing an unloaded association raises or returns `%Ecto.Association.NotLoaded{}` in strict mode. In permissive mode (or with the appropriate config), it fires a new query per access. Each query is fast; 800 sequential queries are not.
- accepted_fix: Preload posts before the loop: `Repo.all(User) |> Repo.preload(:posts)` — 2 queries total.
- rejected_fix_patterns:
  - add DB index on posts.user_id (index likely exists; not the cause of N+1)
  - use raw SQL to fetch everything in one query (works but over-engineered)
  - paginate to fewer users (reduces impact, doesn't fix N+1)

## Evidence Signals

- strongest_signal: `SELECT * FROM posts WHERE user_id = $1` repeated N times in logs; only 1 query should exist for posts (SELECT * FROM posts WHERE user_id IN (...))
- pathognomonic_prove: Telemetry attach counting queries — count equals user_count + 1 (e.g., 801 for 800 users)
- strongest_alternative_explanation: Missing index on posts.user_id
- why_alternative_is_wrong: Each individual query is <5ms (confirmed); the problem is 800 separate queries, not slow queries

## Scoring Notes

- full_credit_conditions:
  - identifies Ecto N+1 from association access in loop without preload
  - explains Ecto does not lazy-load (requires explicit preload)
  - fix adds Repo.preload(:posts) before the loop
  - mentions query count Prove (telemetry or log count)
- partial_credit_conditions:
  - identifies N+1 pattern but suggests pagination as the fix
- fail_conditions:
  - suggests adding DB index as the fix
  - recommends caching the page
