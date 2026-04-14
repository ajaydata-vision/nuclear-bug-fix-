# Repo Guide for Claude

This repo is the **nuclear-bug-fix** skill — a Claude Code skill for
single-shot diagnosis and fix of bugs that survived code review and
multiple fix attempts. The product is `SKILL.md` plus the pattern files
in `references/`. Benchmark cases under `benchmarks/cases/` (one folder
per case, each with `prompt.md`, `evaluator.md`, `verify.md`) grade
single-shot output against ground-truth expectations.

Mean score on the latest self-eval (iteration 4, v1.12): **94.2 / 100**
across 25 cases. The goal is to push that toward 97+ without regressing
any existing case.

---

## BEFORE editing or creating a reference file in `references/`

**Read `docs/reference-authoring-standards.md` once at the start of the
session.** That file contains the full pre-flight / in-flight /
post-flight checklist. The three rules below are the minimum binding
contract — they are non-negotiable and any PR that violates one should
be fixed before merge.

### Rule 1 — Compile Sanity

Every code block in a new reference file MUST compile against a fresh
project for its language/framework/stack. If you cannot run a compiler
or interpreter for the language in this session, state that explicitly
in your response and do not mark the file as complete until a human has
verified the code samples or you have run a compile-check via a
subprocess.

This rule exists because the v1 `dotnet-patterns.md` shipped with
`app.Use<T>()` and `UseTransactionScope` — two APIs that do not exist
and were synthesized from memory. A compile pass would have caught both
in seconds.

### Rule 2 — Version Citations

Every claim of the form "X was added in .NET 7", "EF Core Y changed
behavior Z", "System.Text.Json stack-overflowed on cycles in .NET Core
3.1", etc. MUST link to the release notes URL or the specific package
version where the change happened. If you are not certain, mark the
claim with a `// unverified:` comment instead of stating it
authoritatively. Wrong version history is the second most common defect
class and harder to catch than compile errors because the code still
runs — it just matches the wrong behavior.

### Rule 3 — Adversarial Self-Review Before Commit

After writing a reference file or adding a major section, do a
self-adversarial pass specifically looking for:

1. APIs you wrote from memory that may not exist
2. Version-history claims that may be wrong or misattributed
3. Cross-references to other Categories that may have shifted position
   (e.g. "see Category 11" when you meant Category 4)
4. Fix blocks that don't actually match the Why section
5. `Prove` steps that are not actually provable as written
6. Routing Hints table entries that do not map to an existing pattern
7. Any `[CATEGORY-N]` self-reference inside the same category

The first time this checklist was applied to `dotnet-patterns.md`, it
surfaced 14 defects — 3 red (wrong API / wrong diagnosis) and 11
yellow (noise, wrong version, overstated claims). See the commit log
for `claude/analyze-minimax-skills-jizna` for the full defect list.

---

## Benchmark scoring protocol

Every change to `references/*.md` should be scored against the affected
benchmark cases. See `benchmarks/results/iteration-4-self-eval.md` for
the canonical format. The per-case scoring rubric grades routing,
pattern match, Prove evidence, DDx Gate hypotheses, Verdict confidence,
and BEFORE/AFTER fix code. A typical defect costs 5–12 points.

When adding a new reference file:

1. Add the routing row to `SKILL.md` Phase 2A Domain Classification
   table (around line 214) AND to the reference file guide (around
   line 1085). Both tables must stay in sync.
2. Create at least 5 new benchmark cases for the new domain under a
   fresh prefix (e.g. `DN-001..005` for .NET, `PY-001..005` for
   Python web).
3. Run or hand-score those cases and record the result in
   `benchmarks/results/`.

---

## Current state snapshot

- Latest release: v1.19 (commit `6ee651b` on `main`).
- Latest self-eval: iteration 4 on v1.12, mean 94.2, all 25 cases ≥ 83.
- Active branch: `claude/analyze-minimax-skills-jizna`.
  - 9 deduction-killing precision edits across existing reference files
    (commit `a418bce`).
  - New `references/dotnet-patterns.md`, 12 categories, 37 patterns
    (commit `33417ca`).
  - Adversarial review of dotnet-patterns: 14 technical defects fixed
    (commit `4d65274`).
- Still pending on this branch:
  - Benchmark cases for .NET (`DN-001..N`) — not yet written.
  - MiniMax-AI/skills comparison analysis — deferred.
  - Authoring standards (this file + `docs/reference-authoring-standards.md`).

---

## Conventions

- **One skill, one SKILL.md.** Do not create sub-skills.
- **Reference files are markdown, symptom → why → prove → fix.** Mirror
  the density of `java-patterns.md` (≈833 lines, ~35 patterns).
- **Never commit AI-generated code without running the adversarial
  checklist.** Rule 3.
- **Never delete or downgrade an existing pattern as a "simplification."**
  Every deletion is a coverage regression unless paired with an
  equivalent replacement.
- **Commit messages describe the `why`, not the `what`.** The defect
  being closed is more useful than the files being touched.
