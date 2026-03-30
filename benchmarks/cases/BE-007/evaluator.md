# Evaluator

## Metadata

- id: BE-007
- domain: backend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: orm, join, sql, query, wrong-rows, prisma

## Ground Truth

- root_cause: findMany is called without a where clause filtering on authorId, so it returns all posts with their authors joined.
- why_it_happens: include: { author: true } adds the JOIN to load related author data but does not filter which posts are returned. A separate where clause is required to filter posts by author.
- accepted_fix: Add where: { authorId: userId } to the findMany call.
- rejected_fix_patterns:
  - filter results in JavaScript after fetching all posts
  - add a raw SQL fallback

## Evidence Signals

- strongest_signal: Prisma query log shows no WHERE clause on the posts query
- strongest_alternative_explanation: userId parameter not parsed correctly from the URL
- why_alternative_is_wrong: Adding the where clause with the same userId returns correct results; the parameter is parsed correctly

## Scoring Notes

- full_credit_conditions:
  - identifies missing where clause
  - proposes adding where: { authorId: userId }
  - checks Prisma query log to confirm
- partial_credit_conditions:
  - identifies too many results but filters post-fetch in JS
- fail_conditions:
  - blames Prisma JOIN bug
  - rewrites as raw SQL without explaining the ORM issue
