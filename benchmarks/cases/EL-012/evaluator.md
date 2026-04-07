# Evaluator

## Metadata

- id: EL-012
- domain: elixir-phoenix
- pattern: Ecto unique constraint race
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: ecto, constraint, race-condition, unique-index, toctou, concurrent

## Ground Truth

- root_cause: Time-of-check-to-time-of-use (TOCTOU) race condition. Two concurrent requests for the same email both call `Repo.exists?` and both see the email does not exist (it doesn't yet). Both proceed to `Repo.insert`. The first insert succeeds. The second insert also succeeds — OR raises `Ecto.ConstraintError` if `unique_constraint` is not in the changeset (only the DB index exists). The `Repo.exists?` check is not atomic with the `Repo.insert` — another request can insert between the check and the insert.
- why_it_happens: In concurrent systems, a SELECT followed by an INSERT is not atomic. Two processes can both see the SELECT return false before either has completed the INSERT. The only race-safe uniqueness guarantee is the database unique index, enforced atomically by PostgreSQL during INSERT.
- accepted_fix: Remove the `Repo.exists?` pre-check. Add `unique_constraint(:email)` to the changeset. Let the database enforce uniqueness atomically and handle the `{:error, changeset}` with the unique constraint error.
- rejected_fix_patterns:
  - add a database transaction around the check and insert (doesn't work — SELECT within a transaction still has this race in READ COMMITTED isolation)
  - use a GenServer to serialize all registrations (over-engineered, single point of failure)
  - use SERIALIZABLE transaction isolation (works but overkill and has performance cost)

## Evidence Signals

- strongest_signal: `Repo.exists?` followed by `Repo.insert` — classic TOCTOU; error only under concurrent load; unique index exists (ConstraintError confirms)
- pathognomonic_prove: `tasks = for _ <- 1..5, do: Task.async(fn -> register_user(%{"email" => "test@example.com"}) end); Task.await_many(tasks)` — multiple {:ok, user} results OR Ecto.ConstraintError raised (not caught) confirms race
- strongest_alternative_explanation: Unique index missing from DB
- why_alternative_is_wrong: Ecto.ConstraintError in logs confirms unique index exists and is being hit

## Scoring Notes

- full_credit_conditions:
  - identifies TOCTOU race between Repo.exists? and Repo.insert
  - explains that the check is not atomic with the insert
  - fix removes pre-check and adds unique_constraint to changeset
  - mentions concurrent Task test as Prove
- partial_credit_conditions:
  - identifies the race but suggests serialization via GenServer
- fail_conditions:
  - suggests adding a sleep between check and insert
  - blames database configuration
