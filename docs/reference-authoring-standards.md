# Reference File Authoring Standards

This document is the binding checklist for creating or editing files in
`references/`. It is referenced from `CLAUDE.md` and from `SKILL.md`'s
reference-file guide. Every Claude session that works on a reference
file must read this file once at the start of the session.

Rules marked **[BLOCKING]** prevent the file from being committed.
Rules marked **[ADVISORY]** should be applied but aren't commit blockers.

The defect counts cited throughout come from the adversarial review of
`dotnet-patterns.md` v1 on branch `claude/analyze-minimax-skills-jizna`.
That pass found **14 defects in 958 lines** — roughly 1 defect per
68 lines. Assume the rate is similar for any future reference file
unless a compile pass and this checklist are actively applied.

---

## PRE-FLIGHT (before writing a single line)

### P1. Scope the stack precisely — **[BLOCKING]**

Write a one-sentence scope statement at the top of the file. Example:
*"Covers: ASP.NET Core, DI, async/await, HttpClient, EF Core,
System.Text.Json, Config/IOptions, Kestrel/IIS, concurrency, .NET
version migration. Does NOT cover Blazor or SignalR."*

If the scope is not stated explicitly, scope creep produces a file that
is 60% patterns and 40% drift. The scope statement must include:

- What's in
- What's out (with a one-line reason or a "collect intake and search
  upstream" instruction)
- Version range explicitly supported

### P2. Identify the precedent reference file — **[ADVISORY]**

Every new reference file should mirror the structure of one existing
reference file that handles a similar domain. For enterprise languages
use `java-patterns.md`. For web frontend use `frontend-patterns.md`.
For desktop/IPC use `python-desktop-patterns.md` +
`bridge-adapter-patterns.md`. Mirroring the precedent's density
(~35 patterns over ~830 lines), heading style, and `symptom → why →
prove → fix` template makes Phase 2A routing automatic.

### P3. Draft the category skeleton — **[BLOCKING]**

Before writing any pattern body, draft the 10–15 Category headings
and a one-line intent for each. Example:

```
1. ASP.NET Core middleware pipeline — ordering and lifecycle bugs
2. Model binding & validation — [FromBody] null, culture, [ApiController]
3. DI lifetimes — scoped/singleton capture, IOptions
...
```

A skeleton forces you to commit to coverage scope before getting lost
in any one pattern. If the skeleton has fewer than 10 or more than 15
categories, reconsider — too few is shallow, too many is unreadable.

### P4. Reserve a benchmark prefix — **[ADVISORY]**

Every new reference file should have at least 5 benchmark cases
written against it eventually. Reserve a 2-letter prefix in
`benchmarks/cases/` (e.g. `DN-001..005` for .NET, `PY-001..005` for
Python web, `GO-001..005` for Go). Document the prefix choice at the
top of the reference file as a comment so the next author does not
collide.

---

## IN-FLIGHT (while writing patterns)

### F1. Every pattern uses the four-section template — **[BLOCKING]**

```
### Pattern: <short imperative title — no trailing period>
**Symptom:** <what the user sees, verbatim-grade specificity, error
messages in code ticks>
**Why:** <root cause mechanism, including the alternative explanations
that are commonly mistaken for this one and why they are wrong>
**Prove:** <an operation the user can run RIGHT NOW to confirm or
eliminate this hypothesis — not "read the code carefully">
**Fix:** <BEFORE/AFTER code, or a precise sequence of steps>
```

No shortcuts. A pattern missing `Prove` becomes advice, not diagnosis.
A pattern missing `Why` becomes a recipe with no transferability to
adjacent bugs.

### F2. Compile every code sample — **[BLOCKING]**

Every `csharp`, `java`, `python`, `js`, `ts`, `elixir`, `go`, `php`,
`rust`, `kotlin`, `swift` code block must compile against a fresh
project for its stack. Acceptable compile-verification methods, in
decreasing order of confidence:

1. **Run the compiler directly in a sandbox.** If this session has
   `dotnet`, `javac`, `tsc`, `go build`, `mix`, `php -l`, `python -c`,
   etc. available, run them against every new code block.
2. **Copy-paste each code block into a minimal `Program.cs` /
   `Main.java` / `index.ts` file in `/tmp` and run the compiler.**
3. **Use an MCP tool that runs the stack's build command.**
4. **Manual expert review** — only acceptable if #1–3 are unavailable,
   AND the author explicitly flags this in the commit message with
   "code samples not compile-verified; review before merge."

**Never skip this for a code block that declares an API.** The
`app.Use<T>()` and `UseTransactionScope` defects in `dotnet-patterns.md`
v1 were exactly this — APIs synthesized from memory that don't exist,
that a one-minute compile check would have caught. You don't have to
know every framework; you have to verify what you wrote.

### F3. Version claims need sources — **[BLOCKING]**

Any claim of the form "X was added in version Y" or "X changed
behavior in version Y" must satisfy one of:

- **Inline citation** — link to the release notes URL or the
  `CHANGELOG.md` entry on GitHub: `([Npgsql 6.0 release notes](https://...))`.
- **`// unverified:`** — state the claim hedged, not authoritatively.
  Example: `// unverified: I believe this was added in EF Core 6; check
  the docs before relying on this.`
- **Exact package-version range** — `"This behavior applies to
  Npgsql >= 6.0.0"` is acceptable without a link if the version is
  precise enough that a reader can confirm it with one `dotnet list
  package` command.

The historical-fact defects in `dotnet-patterns.md` v1 ("EF Core 5+
with UseLazyLoadingProxies" — actually 2.1+; ".NET Core 3.1
stack-overflowed on cycles" — actually threw `JsonException`; "Npgsql
6.0 strict UTC triggered by .NET upgrade" — actually triggered by the
Npgsql package bump) were wrong in ways that would mislead a reader to
the wrong root cause. Every one of these would have been caught by
rule F3.

### F4. Alternative hypotheses in every `Why` — **[ADVISORY]**

The best `Why` sections include the one or two explanations most
likely to be mistaken for the real cause, each paired with why it is
wrong. Example from `java-patterns.md`:

> **Why:** ... A `[Timestamp]` column would also produce this
> symptom, but the entity is detached and the row version was never
> loaded, so that's not it.

This directly feeds the DDx Gate in Phase 3.9 and is often the
difference between a 92 and a 100 on a benchmark case.

### F5. Every `Fix` includes a `Do NOT:` block — **[ADVISORY]**

The common wrong fixes are as informative as the right one. State them
explicitly. Example:

> **Do NOT:** wrap the call in `Task.Run(() => x.Result).Result` to
> "hide the sync context" — that burns a thread-pool thread to block
> another thread-pool thread and causes starvation. The real fix is
> async propagation.

Benchmark evaluators frequently test for rejection of common wrong
fixes (see `rejected_fix_patterns` in `evaluator.md` files). A pattern
that names and rejects the wrong fix earns points even on cases that
test for wrong-fix resistance.

### F6. Prove steps must be actually runnable — **[BLOCKING]**

"Read the code carefully" and "check if the configuration is correct"
are not provable. A Prove step must specify:

- An exact command, log query, counter, or code change to make
- What output specifically confirms the hypothesis
- What output specifically eliminates the hypothesis

Example (correct):
> **Prove:** `dotnet-counters monitor System.Runtime` during the slow
> period. If `threadpool-thread-count` is growing linearly while
> `threadpool-queue-length` is also high → starvation confirmed. If
> queue length is 0 → look elsewhere.

Example (wrong):
> **Prove:** Check the thread pool status.

---

## POST-FLIGHT (adversarial self-review before commit)

Run this checklist after the file is written but before the git commit.
It is directly grounded in the 14 defects found in `dotnet-patterns.md`
v1. The pass took roughly 30 minutes and saved a benchmark score hit
of ~5 points.

### R1. API reality check — **[BLOCKING]**

Grep every code block for method / class / property names you wrote
from memory. For each one, verify it actually exists in the framework
at the version the file targets. Flag anything you had to "think
about" — those are the ones most likely invented.

**Defects of this class caught in the dotnet review:**
- `app.Use<MyMiddleware>()` — synthesized from `app.UseMiddleware<T>()`
- `UseTransactionScope()` — plausible but not a real API
- `o.SuppressAsyncSuffixInActionNames = false` presented as a way to
  apply `[ApiController]` globally — unrelated options

**How to catch:** paste each questionable identifier into the target
framework's documentation search. If the first hit is a Stack Overflow
question from someone also trying to find it, it probably doesn't exist.

### R2. Version-history audit — **[BLOCKING]**

For every claim of the form "X was added/changed in version Y",
verify by one of:

- Searching the `CHANGELOG.md` or release notes of the package/framework
- Running `dotnet list package` / `npm ls` / equivalent in a minimal
  reproduction
- Checking the GitHub repository's tag list for when the feature
  appears in the source

**Defects of this class caught in the dotnet review:**
- "EF Core 5+ with `UseLazyLoadingProxies`" — actually EF Core 2.1+
- "STJ before .NET 7 cannot populate records" — actually STJ 5 already
  supports parameterized constructors on records; .NET 7 added the
  `required` keyword specifically
- ".NET Core 3.1 stack-overflowed on cycles" — actually threw
  `JsonException` from 3.0 onward
- "ValidateScopes only in Development and only if explicitly opt in" —
  actually on by default in Development since .NET 6
- "Npgsql UTC bug triggered by .NET upgrade" — actually triggered by
  Npgsql package version 5 → 6, independent of .NET version

### R3. Cross-reference check — **[BLOCKING]**

Grep the file for every `(see Category N)`, `(see the X pattern)`, or
`(see references/Y.md)`. Verify each target exists and is accurate.

**Defects of this class caught in the dotnet review:**
- "(see Category 11)" for ThreadPool starvation — starvation lives in
  Category 4, the same section

### R4. Namespace / import check — **[ADVISORY]**

For every non-trivial code sample, check whether the types used
require any `using` directive that a reader would not have by default.
Flag ambiguities between competing namespaces.

**Defects of this class caught in the dotnet review:**
- `new IPNetwork(...)` — .NET 8 added `System.Net.IPNetwork` which
  collides with `Microsoft.AspNetCore.HttpOverrides.IPNetwork` and
  produces a `CS0104` ambiguous reference compile error

### R5. Routing Hints table sync — **[BLOCKING]**

If the file has a routing hints table at the bottom (or similar), every
row must map to an actual pattern in the file. Every pattern with a
distinctive symptom should appear as a row.

**How to check:** generate the row count from `grep -c '^### Pattern:'`
and compare to the routing-hints table row count. Drift means some
patterns are not searchable by symptom.

### R6. SKILL.md wiring check — **[BLOCKING]**

When adding a new reference file, the `.NET` (or equivalent) row must
be added to BOTH:

1. `SKILL.md` Phase 2A Domain Classification table (around line 214)
2. `SKILL.md` Reference File Guide (around line 1085)

A file in `references/` that is not wired into Phase 2A is invisible
to Phase 2A pattern pre-load and will never route. This is the single
highest-leverage hookup for single-shot performance.

### R7. Fix-block completeness — **[ADVISORY]**

For every pattern, verify:

- BEFORE/AFTER code or clearly-labeled multi-step fix procedure
- Explicit "Do NOT" block naming the common wrong fix
- If the fix requires touching config (appsettings.json, web.config,
  .csproj, application.yml), include the exact snippet

### R8. Symptom-specificity check — **[ADVISORY]**

Every `Symptom` should include at least one of:

- An exact error message in quotes or code ticks
- An exact log line
- A specific reproducible observable (e.g. "the counter shows 3
  instead of 4", "the response is a 204 with an empty body")

Vague symptoms like "the app is slow" or "something is wrong" route
nowhere in Phase 2A.

### R9. Red-team your own Why sections — **[ADVISORY]**

For each `Why`, ask: "if the root cause were actually X (the most
likely alternative), what would I write differently?" If the answer is
"nothing much," the Why is too vague and the pattern won't beat the
DDx Gate in Phase 3.9.

### R10. Final grep pass — **[BLOCKING]**

Run this grep on every new reference file before committing:

```bash
grep -n "TODO\|FIXME\|XXX\|<insert\|<fill\|placeholder\|verify this\|check this\|unverified:" references/<your-file>.md
```

Zero matches = ready. Any match = either finish it or explicitly flag
in the commit message.

---

## DEFECT TAXONOMY (for triaging future reviews)

All 14 defects caught in the `dotnet-patterns.md` v1 review fell into
6 categories. Use this to triage future adversarial passes — not all
defects are equal.

| Severity | Category | Rule it would have caught | Example |
|---|---|---|---|
| 🔴 | Non-existent API | R1 | `app.Use<T>()`, `UseTransactionScope` |
| 🔴 | Wrong root-cause diagnosis | R9 | "ASP.NET Core buffers IAsyncEnumerable" |
| 🔴 | Wrong fix recommendation | F5 + R7 | "UseStatusCodePages fixes CORS on 401" |
| 🟡 | Wrong version history | F3 + R2 | "EF Core 5+ with UseLazyLoadingProxies" |
| 🟡 | Wrong cross-reference | R3 | "(see Category 11)" when it's Category 4 |
| 🟡 | Unrelated noise in fix | F5 + R7 | `LowercaseUrls = true` inside a DateTime fix |

Red defects are commit-blockers. Yellow defects should be fixed but a
file with only yellow defects can ship and be corrected in a follow-up.

---

## WHAT THIS DOCUMENT DOES NOT DO

It does not guarantee a defect-free reference file. It guarantees that
the most common defect classes — invented APIs, wrong version history,
wrong cross-references, unprovable Prove steps, broken wiring — are
caught before commit. Novel defects will still slip through; that's
why `benchmarks/cases/` and self-eval exist.

It also does not replace human review of security-sensitive code,
architectural trade-offs, or style. This is a floor, not a ceiling.
