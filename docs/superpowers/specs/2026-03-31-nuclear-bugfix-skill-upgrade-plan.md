# Nuclear Bug Fix Skill Upgrade — Python Scraping/LLM Pipeline Stack

**Date:** 2026-03-31
**Scope:** Full overhaul (C) — patterns, methodology, benchmarks
**Target stack:** Python 3.13 + Playwright + httpx + pdfplumber + LLM multi-tier fallback + Rich terminal UI
**Goal:** Push single-shot fix confidence from ~70% to 90% for this stack family
**Revision:** v4 — post adversarial review of v3 plan, with bundle-based claim validation

---

## Claim Discipline

This plan targets a **stack-family specialization** inside `nuclear-bug-fix`, not a
global rewrite of the skill's universal methodology.

- The upgrade should materially improve single-shot diagnosis for the targeted
  Python scraping / LLM pipeline / terminal UI stack family.
- The skill must still remain correct for non-target stacks; stack-specific
  guidance must be routed, not made universal by accident.
- The `90%` single-shot claim is a **benchmark gate**, not a wording change.
  It can only be claimed after the post-upgrade benchmark protocol in D9 passes.
- The `90%` claim must be earned on a **fixed, versioned claim slice** with
  repeat runs, fixed assets, and a frozen no-regression slice. No ad hoc case
  selection is allowed.
- Claim-mode runs must execute against a **full skill bundle snapshot**, not a
  live working tree file. The benchmark artifact must mirror the shipped skill
  layout closely enough that install/update compatibility is preserved.
- The public `90%` claim slice must contain only cases marked
  `one_shot_eligible: true`; timing-sensitive cases are allowed only when the
  evaluator marks them as controlled/deterministic and the assets prove the
  reproduction amplifier.

---

## Actual Bug Distribution (from git history, 27 fixes)

| Category | Fix Count | % | Plan Coverage |
|---|---|---|---|
| Rich/Live terminal display | 13 | 48% | D1.5 (NEW — was missing in v1) |
| Playwright/scraping | 8 | 30% | D1 |
| LLM/API | 3 | 11% | D2 (reduced — was over-scoped in v1) |
| File/path/encoding | 3 | 11% | D4 |

---

## Evidence Traceability (Required Before Final Sign-Off)

The current distribution table is directionally useful, but the final upgrade
must be reproducible by maintainers who were not present for this review.

- Append a short evidence appendix listing the 27 source fixes, their category
  mapping, and the commit/code location used to justify each new pattern.
- Record the git query / selection rule used to derive the distribution so the
  breakdown can be regenerated when the bug mix changes.
- Every new benchmark case must cite the source commit or code location that
  motivated it.

---

## Gaps Identified (Adversarial Review v2)

| Gap | Current Coverage | Impact | Severity |
|---|---|---|---|
| Rich/Live terminal stdout ownership bugs | No reference file | 48% of all bugs in this codebase | CRITICAL — was entirely missed in v1 |
| Browser automation / scraping bugs | No reference file | 30% of bugs — Playwright DOM, overlays, React internals | HIGH |
| Multi-tier LLM fallback chain visibility | No reference file (but tier tracking already exists in code) | 11% of bugs — tier IS tracked but buried in DEBUG | MEDIUM — was overstated in v1 |
| Intentional vs accidental error suppression | One generic pattern in bug-patterns.md | Not all bare excepts are bugs — need decision tree | MEDIUM — was overstated in v1 |
| Rate limiter ephemeral state | Not covered | In-memory state lost on restart | MEDIUM |
| Document extraction edge cases | Not covered | Password PDFs, scanned PDFs, encoding | LOW |
| Debuggability scoring / pre-audit | Not in methodology | No codebase audit before diagnosis | MEDIUM |

### v1 Corrections Applied

| v1 Claim | Reality | Change |
|---|---|---|
| "34 silent swallow blocks" | ~7 genuinely problematic; rest are intentional fire-and-forget (overlay dismiss, callback protection, cleanup) | Reframe pattern as decision tree |
| "Silent Tier Switching" as D2 #1 | `_llm_tier` already tagged on every result + tier skips logged at INFO | Reframe: "tier buried in DEBUG, not INFO" |
| "Greedy regex = data corruption" HIGH | `json.loads` validation gate catches most corrupt matches | Downgrade to MEDIUM |
| "6 LP benchmark cases" | Only 3 actual LLM bugs in history — 6 cases over-represents | Reduce to 4, add 4 TU cases |
| Rich/Live bugs = 0 coverage | 13 bugs (48% of total) — biggest bug family | Add D1.5 + 4 TU benchmark cases |

---

## Deliverables

### D1. New Reference File: `references/scraping-automation-patterns.md`

Patterns from Playwright browser automation and web scraping. Sourced from commits: 553ce0b, 0a8a114, f6a1c0f, 34b750e, 1b7fbf0, e4886ad, 9c00d37, 130db39.

**Categories:**

1. **Overlay/Modal Interference** — click absorbed silently by Radix backdrop, feedback dialog, chat widget
   - Source: f6a1c0f (overlay rewrite), 553ce0b (React crash from el.remove)
2. **React Internals Manipulation** — `__reactProps` fiber walking, version-fragile, silent fallthrough to DOM click
   - Source: 553ce0b (Calendar Tenders card click via React onClick)
3. **Date Picker / Calendar Navigation** — manual DOM walking for shadcn/Radix rdp components, class token matching vs substring matching
   - Source: f6a1c0f (Tailwind arbitrary selector false-match on "outside")
4. **Session/View State Persistence** — "Closed Tenders" view hijacks results, session storage persists across page loads
   - Source: 553ce0b, 0a8a114 (page reload before each download)
5. **Download Handling** — 0-byte ZIPs, timeout before download completes, no download button on detail page
   - Source: 9c00d37 (smart wait replacing fixed 5.5s sleep)
6. **Stale Element Reference** — element found by locator, page mutates (React re-render), interaction throws
7. **Scroll-to-Load / Infinite Scroll** — total count mismatch, elements not in DOM until scrolled into view
8. **Anti-Bot / Rate Limiting** — CAPTCHA mid-session, 403 after N requests, empty response body
9. **Selector Fragility** — text-based selector matches nav card instead of tab panel, class-based breaks on build
   - Source: 553ce0b (get_by_text matched "Today Tenders" card instead of date tab)
10. **Viewport / Headless Mode** — element not visible in headless without explicit viewport, scroll needed before click
    - Source: e4886ad (1920x1080 viewport), 1b7fbf0 (scroll into viewport before click)

Each pattern: symptom, why, how to prove, how to fix.

### D1.5. New Reference File: `references/terminal-ui-patterns.md`

Patterns from Rich/blessed/curses terminal UI frameworks fighting with stdout/stderr ownership. Sourced from 13 commits: 0028b5f, e5a2284, b90930e, 2d5ea1b, b4781cf, d14d1aa, 2dc40f5, 30ffa32, 6a5d761, 6a5ac59, 089bef1.

**Categories:**

1. **stdout Ownership Conflict** — Rich Console, logging StreamHandler, and module print() all write to sys.stdout; Live display assumes exclusive ownership
   - Source: 30ffa32 (Console writes to devnull during Live)
2. **Live.update() Silent Failure** — Live renders to nowhere when sys.stdout redirected to devnull; no error raised
   - Source: b90930e (devnull redirect breaks Live.update)
3. **Dynamic-Height Renderable on Windows** — ANSI cursor-up fails when table row count changes between renders; causes duplicate frames scrolling up
   - Source: 0028b5f (nuclear fix: drop Live for analyzer, use direct prints)
4. **Auto-Refresh Timer vs Callback Updates** — 4Hz timer and callback-driven updates race; burst of cached results causes line spam
   - Source: b4781cf (kill timer), 2d5ea1b (render only on callbacks), e5a2284 (throttle renders)
5. **Import-Time StreamHandler Capture** — module-level logging.StreamHandler created at import time; handler swap after import misses it
   - Source: 30ffa32 (swap_log_handlers after lazy import)
6. **force_terminal Flag** — Rich Console defaults to dumb terminal on some Windows configs; in-place updates require force_terminal=True
   - Source: d14d1aa (force_terminal=True)
7. **Blocking update() Inside Callback** — calling live.update() from within a callback that Live itself triggered creates deadlock with auto-refresh lock
   - Source: 2dc40f5 (remove blocking live.update from callbacks)
8. **Log Handler Routing Through RichHandler** — routing module loggers through RichHandler during Live display causes double-rendering and interleaved output
   - Source: 6a5ac59 (suppress console handlers instead of routing through Rich)

Each pattern: symptom, why, how to prove, how to fix.

### D2. New Reference File: `references/llm-pipeline-patterns.md`

Patterns from multi-tier LLM API fallback chains. Sourced from tender_analyzer.py code and commits: 85a05c0, bace2c0, 9bd68e9, 35bff53.

**Categories (reduced from 10 to 8 after v1 review):**

1. **Tier Decision Buried in DEBUG** — `_llm_tier` tagged on result but only visible at DEBUG level or in callbacks, not in INFO log stream
   - Reframed from v1 "Silent Tier Switching" — tracking EXISTS but is not surfaced
2. **Rate Limiter State Loss** — in-memory GroqRateLimiter/GeminiRateLimiter reset on crash/restart, causes immediate 429 cascade on all tiers
3. **JSON Fallback Parser Edge Cases** — greedy regex `\{.*\}` DOTALL as fallback after json.loads fails; MEDIUM risk because json.loads on matched group acts as validation gate, but can still fail on multi-object responses
   - Downgraded from v1 HIGH — validation gate catches most cases
4. **LLM Returns 200 With Error Body** — status code OK but response body contains error message or empty content field; client only checks status code
5. **Prompt Truncation** — input exceeds model context window, model silently processes truncated input, answer based on partial document
6. **Token Estimation Drift** — `len(prompt) // 4` rough estimate diverges from actual tokenization; rate limiter allows calls that exceed real TPM
7. **Fallback Chain Masks Root Cause** — tier 1 auth error, tier 2 rate limit, tier 3 wrong answer — each tier's error logged at WARNING but user only sees final output with no summary of what failed
8. **Response Validation Too Loose** — `validate_llm_response` checks `verdict` key exists and value is in allowed set, but doesn't check semantic quality (hallucinated scope_summary, wrong domain classification pass validation)

Each pattern: symptom, why, how to prove, how to fix.

### D3. Update: `references/bug-patterns.md`

Add/strengthen in existing categories:

- **Category 7 (Interception Layers):** New pattern — **"Intentional vs Accidental Error Suppression"** — decision tree for when bare `except: pass` is acceptable (overlay dismiss, cleanup in finally, UI callback protection) vs when it hides real bugs (data path, parse results, cache operations). Include: grep audit command, classification criteria, remediation priority.
  - Reframed from v1 "Error swallowing graveyard" — not all bare excepts are bugs
- **Category 10 (Logic & Algorithm):** Strengthen "Greedy regex" pattern with LLM JSON fallback extraction case. Note: severity is MEDIUM when followed by json.loads validation, HIGH when regex match is used directly without re-parsing.
- **Category 4 (Network & API):** New pattern — **"Multi-tier fallback hiding root cause"** — cascading API calls where each tier's error is logged individually but no summary shows the full chain of failures.
- **Category 5 (Environment & Config):** New pattern — **"Config parser silent defaults"** — configparser `.get(fallback=...)` / dotenv defaults / yaml `get(key, default)` returning fallback values when section/key is missing. No error raised. Code runs with wrong config silently.

### D4. Update: `references/backend-patterns.md`

Add to existing categories:

- **Category 7 (Rate Limiting):** New pattern — **"Rate limiter ephemeral state"** — in-memory rate tracking (token windows, daily counters, cooldown timestamps) lost on process restart/crash. Restart causes immediate quota exhaustion on all tiers because limiter thinks it has full budget.
- **Category 5 (File Handling):** New pattern — **"Document extraction silent failure"** — PDF password-protected returns empty string, scanned/image PDF returns near-zero text without error, HTML with wrong encoding returns garbled text, DOCX with only table data misses content. All return empty/partial string, no exception raised.

### D5. Update: `SKILL.md` — Methodology Upgrades

**5a. Phase 2A Domain Classification — Add three new domains:**

| Domain | Signals | Reference File |
|---|---|---|
| **Scraping / Browser Automation** | Playwright, Selenium, Puppeteer, scraper returns empty, click not working, download fails, overlay blocks interaction, selector not found, stale element | `references/scraping-automation-patterns.md` |
| **LLM Pipeline / Multi-Model** | LLM returns wrong answer, API 429, fallback chain, JSON parse error, token limit, model drift, rate limiting, prompt truncation | `references/llm-pipeline-patterns.md` |
| **Terminal UI / Live Display** | Rich Live display, blessed, curses, terminal output corruption, line spam, stdout redirect, in-place update broken, handler conflict, force_terminal | `references/terminal-ui-patterns.md` |

**5b. Phase 2C Symptom-to-Category Map — Add new rows:**

| Symptom Signal | Root Cause Category |
|---|---|
| Scraper returns empty results after site worked yesterday | Upstream site change / selector drift / anti-bot trigger |
| Click fires but nothing happens in browser automation | Overlay/modal intercepting / wrong element / React zone bypass needed |
| LLM analysis wrong for some inputs but not others | Prompt truncation / wrong tier answered / response parsing edge case |
| All API tiers fail after restart | Rate limiter state lost / ephemeral in-memory tracking |
| Download starts but file is 0 bytes or corrupt | Download not awaited / timeout before completion / partial write |
| Terminal output corrupted, duplicate lines, or line spam | Live display stdout ownership conflict / auto-refresh race / dynamic height overflow |
| Live display shows nothing, no error | sys.stdout redirected / Console created on wrong file object / force_terminal missing |
| Log output disappears during Live display | StreamHandler created at import time before handler swap / logs routed to wrong sink |

**5c. New Phase 0.5 — Debuggability Pre-Audit:**

Before diving into diagnosis, score the codebase's **instrumentation readiness**
for this stack family. This determines whether you can diagnose efficiently or
whether you must instrument first.

Important constraints:

- This is an **internal pre-audit**, not user-facing verdict language.
- This is **stack-scoped** to Python scraping / browser automation / LLM
  pipeline / terminal UI problems.
- This does **not** replace the DDx Gate. The DDx Gate remains the only place
  that assigns verdict confidence.

```
DEBUGGABILITY SCORING (run in 2 minutes, before Phase 1):

1. SILENT SWALLOW COUNT
   Run a stack-appropriate suppression audit.
   For Python-first repos, use rg/grep to find bare or blanket exception
   handlers and classify them.
   Count exception handlers that do not log or surface failure.
   Classify each: intentional fire-and-forget (overlay, cleanup, UI callback)
   vs data-path (parsing, caching, API calls, file I/O).
   Data-path silent swallows are the ones that matter.
   0-2 data-path = GREEN, 3-10 = YELLOW, 11+ = RED

2. ERROR CHAIN VISIBILITY
   Can you trace which code path produced a given output?
   Full trace = GREEN, Partial = YELLOW, No trace = RED

3. LOG COVERAGE AT DECISION POINTS
   Are key decisions logged? (which branch taken, which tier used, what value compared)
   All logged = GREEN, Some = YELLOW, None = RED

4. REPRODUCTION INFRASTRUCTURE
   Can you replay a failure offline? (saved inputs, cached responses, snapshots)
   Full replay = GREEN, Partial = YELLOW, None = RED

5. OUTPUT CHANNEL OWNERSHIP
   Is it clear which system owns stdout/stderr at each phase?
   Single owner per phase = GREEN
   Multiple writers but coordinated = YELLOW
   Uncoordinated (print + logging + UI framework + subprocess) = RED

READINESS:
  READY    = 5 GREEN
  PARTIAL  = 1-2 YELLOW and no RED
  BLOCKED  = Any RED

If readiness is PARTIAL:
  -> Add or surface logs at the weak decision points before running Phase 3.

If readiness is BLOCKED:
  -> Add forensic logging / snapshots at RED areas BEFORE running Phase 3.
  -> Do not issue a high-confidence diagnosis until the blocked evidence path
     is instrumented.
```

**5d. Phase 4 — Deep Pattern Reference (must be updated, not just Phase 2):**

Add the new files to the Phase 4 routing table and co-loading guidance:

| File | When to Load | Contents |
|---|---|---|
| `references/scraping-automation-patterns.md` | Playwright/Selenium/Puppeteer/browser automation/scraper interaction failures | Overlay interference, selector drift, session/view state, download handling, stale DOM state, anti-bot, viewport/headless |
| `references/llm-pipeline-patterns.md` | Multi-tier LLM pipelines, fallback chains, rate limiting, response parsing, prompt truncation, token budget drift | Tier visibility, fallback masking, validation gaps, 200-with-error-body, prompt/token limits |
| `references/terminal-ui-patterns.md` | Rich/blessed/curses terminal UI, stdout/stderr ownership, in-place render corruption, handler conflicts | Live ownership, dynamic-height rendering, handler ordering, force_terminal, callback/timer races |

Add co-loading rules:

- Scraping + backend/API symptoms: load `references/scraping-automation-patterns.md` and `references/backend-patterns.md`
- Scraping + provider/site drift: load `references/scraping-automation-patterns.md` and `references/external-intelligence.md`
- LLM pipeline + rate limiting / API auth: load `references/llm-pipeline-patterns.md` and `references/backend-patterns.md`
- LLM pipeline + version/provider drift: load `references/llm-pipeline-patterns.md` and `references/external-intelligence.md`
- Terminal UI + timing/race symptoms: load `references/terminal-ui-patterns.md` and `references/intermittent-race-bugs.md`
- End-to-end Python tender pipeline bugs may require all of:
  `references/scraping-automation-patterns.md`,
  `references/llm-pipeline-patterns.md`,
  `references/terminal-ui-patterns.md`,
  plus `references/backend-patterns.md` or `references/bug-patterns.md`

**5e. Update SKILL.md description/triggers:**

Add to the trigger list: "scraper returns empty", "wrong LLM response", "API rate limited",
"Playwright click not working", "download fails silently", "terminal output corrupted",
"Live display broken", "Rich display not updating", "line spam in terminal".

### D6. New Benchmark Cases (14 cases → total 159)

**SA-xxx (Scraping/Automation) — 6 cases:**

| Case | Bug Type | Pattern | Source Commit |
|---|---|---|---|
| SA-001 | Overlay absorbs Playwright click silently | Bohrbug — overlay interference | f6a1c0f |
| SA-002 | Session view state persists, "Closed Tenders" hijacks results | Bohrbug — stale view | 553ce0b |
| SA-003 | React `__reactProps` key renamed in minor version | Regression — React internals | 553ce0b |
| SA-004 | Date picker class token matching vs Tailwind substring matching | Bohrbug — selector fragility | f6a1c0f |
| SA-005 | Download returns 0-byte ZIP, no error raised | Bohrbug — download not awaited | 9c00d37 |
| SA-006 | Text selector matches nav card instead of tab panel | Bohrbug — selector ambiguity | 553ce0b |

**LP-xxx (LLM Pipeline) — 4 cases (reduced from 6):**

| Case | Bug Type | Pattern | Source |
|---|---|---|---|
| LP-001 | Greedy regex `\{.*\}` fallback parser edge case | Bohrbug — MEDIUM (has validation gate) | tender_analyzer.py:790 |
| LP-002 | Rate limiter state lost on restart, all tiers 429 | Bohrbug — ephemeral state | tender_analyzer.py:120-172 |
| LP-003 | Tier decision buried in DEBUG, not visible at INFO | Bohrbug — observability gap | tender_analyzer.py:1237-1290 |
| LP-004 | Prompt exceeds context window, silently truncated | Bohrbug — prompt truncation | tender_analyzer.py:97 GROQ_MAX_TOKENS_INPUT |

**TU-xxx (Terminal UI) — 4 cases (NEW in v2):**

| Case | Bug Type | Pattern | Source Commit |
|---|---|---|---|
| TU-001 | Live.update() silent failure when stdout is devnull | Bohrbug — stdout ownership | b90930e |
| TU-002 | Dynamic-height renderable ANSI cursor-up overflow on Windows | Bohrbug — platform terminal escape | 0028b5f |
| TU-003 | Import-time StreamHandler survives handler swap | Bohrbug — import side effect | 30ffa32 |
| TU-004 | Auto-refresh timer races with callback updates → line spam | Intermittent — timing | b4781cf, e5a2284 |

Each case follows `CASE_TEMPLATE.md` format: prompt.md, evaluator.md, assets/, verify.md.

### D6.5. Stretch Cases Required Before Claiming `90%`

The 14 core cases are enough to validate that the new domains are real and
useful. They are **not** enough by themselves to justify a `90%` single-shot
claim for the stack family. The claim gate must use a larger, asset-backed
targeted slice that closes the domain-count gap in D7.

Add these stretch cases before using the `90%` claim publicly:

- `SA-007` anti-bot / CAPTCHA / 403 drift mid-session
- `SA-008` stale element after re-render / DOM mutation
- `SA-009` headless vs headed / viewport mismatch
- `SA-010` scroll-to-load / infinite-scroll omission
- `SA-011` provider/site drift breaks selector after UI update
- `SA-012` detail-page variant missing primary download button / alternate flow
- `LP-005` HTTP 200 with error body / empty content payload
- `LP-006` response validation too loose / semantically wrong pass
- `LP-007` token estimation drift allows calls that exceed real quota budget
- `LP-008` fallback chain masks root cause because no consolidated failure summary is surfaced
- `TU-005` `force_terminal` missing on Windows / dumb terminal fallback
- `TU-006` callback-triggered update deadlock / re-entrant render path
- `TU-007` RichHandler routing causes duplicate/interleaved renders during Live
- `TU-008` print/logging/subprocess output corrupts in-place terminal ownership

This expands the claim gate slice from 14 to 28 cases and closes the highest
remaining risk gaps in D1, D1.5, and D2.

### D6.6. Asset Requirements For Claim Cases

To make the `90%` claim defensible, the claim-gate cases must be backed by raw
evidence, not only summarized prompts.

Required case asset rules:

- Every D6.5 stretch case must include an `assets/` directory.
- Every case in the public `benchmarks/slices/python-pipeline-claim-28.txt`
  manifest must include an `assets/` directory.
- The public 28-case claim slice must be **100% asset-backed**. If a core case
  lacks assets, backfill them before any claim-mode run.
- Prompts should stay concise; the decisive clues should live in raw artifacts,
  not answer-revealing narration.

Recommended asset types by domain:

- Scraping / browser automation: DOM excerpt or saved HTML fragment, screenshot
  showing overlay / wrong tab / missing element, network response or download
  metadata, optional Playwright trace excerpt.
- LLM pipeline: raw API response body, rate limiter state snapshot or cooldown
  log, prompt length / token budget evidence, fallback-chain log excerpt.
- Terminal UI: stdout/stderr capture transcript, Windows vs non-Windows console
  transcript when relevant, logger/handler dump, frame capture showing
  corruption or duplication.

Every evaluator should explicitly name which asset contains the strongest signal.

Public claim slice eligibility rules:

- Every case in `python-pipeline-claim-28.txt` must be marked
  `one_shot_eligible: true`.
- Cases in the public claim slice must have `determinism: high` or
  `determinism: controlled`.
- If a case comes from an intermittent/timing family, the evaluator and assets
  must document the amplifier that makes the reproduction controlled enough for
  a single-shot public claim.

### D7. Update: `benchmarks/COVERAGE_MATRIX.md`

Add new domain rows:

| Domain | Benchmark Families | Target Cases |
|---|---|---|
| Scraping / Browser Automation | overlay interference, selector drift, download handling, session state, React internals, anti-bot, scroll loading, viewport/headless | 12 |
| LLM Pipeline / Multi-Model | tier visibility, rate limiter state, JSON parsing, prompt truncation, token estimation, response validation, fallback masking | 8 |
| Terminal UI / Live Display | stdout ownership, dynamic-height rendering, auto-refresh timing, handler swap ordering, force_terminal, platform-specific escape codes | 8 |

Add to Stack Families list:
- Playwright
- httpx
- pdfplumber
- python-docx
- beautifulsoup4
- Groq API
- Gemini API
- Ollama
- Rich (terminal UI)
- openpyxl

### D8. Update: `benchmarks/index.yaml`

Add new domain entries:
```yaml
  - id: scraping-automation
    description: Playwright/Selenium browser automation, overlay interference, selector drift, download handling, session state, React internals.
    current_cases: 12
  - id: llm-pipeline
    description: Multi-tier LLM fallback chains, rate limiter state, JSON parsing, prompt truncation, tier visibility, response validation.
    current_cases: 8
  - id: terminal-ui
    description: Rich/blessed/curses terminal UI, stdout ownership, Live display, dynamic-height rendering, auto-refresh timing, handler swap.
    current_cases: 8
```

Update `current_case_count: 173`.

### D8.5. Benchmark Harness Improvements (Now In Scope)

The current harness is not sufficient to support a defensible before/after
claim. Improve the harness so baseline-vs-candidate comparisons are executable,
reproducible, and tied to a full skill bundle snapshot rather than a live repo
file.

Required harness changes:

- Add `--skill-bundle` as the primary claim-mode input. `--skill-md` may remain
  as a local debugging fallback, but it is **not** valid for public claim runs.
- The bundle/snapshot layout must be explicit and checked in by convention:

  ```text
  benchmarks/skill_snapshots/<snapshot-id>/
    manifest.json
    skill/
      SKILL.md
      references/
      scripts/        # optional, included when parity/update checks need them
  ```

- `manifest.json` must record at minimum:
  - snapshot id
  - creation timestamp
  - source commit
  - source kind (`repo`, `archive`, or `installed`)
  - archive/hash metadata when the snapshot came from `dist/nuclear-bug-fix.skill`
  - bundle entrypoint (`skill/SKILL.md`)
  - exact reference file inventory included in the snapshot
- The benchmark snapshot must mirror the shipped skill layout under `skill/`.
  Do not invent a benchmark-only layout that diverges from the install/update
  artifact shape.
- Snapshot creation must support both:
  - repo-root staging using the same top-level allowlist as the installer/packager
  - extraction from a built `dist/nuclear-bug-fix.skill` archive
- Benchmark bundle support must not require breaking changes to the shipped
  installer/updater layout. If packaging/allowlist code is touched, updater
  smoke tests remain mandatory.
- Add `--results-prefix` or equivalent so baseline and candidate runs do not
  overwrite each other.
- Add `--cases-file` support so a frozen case manifest can define the exact
  slice under test.
- Add `--subject-model` and `--scoring-model` overrides so claim runs record the
  exact models used.
- Add `--runs N` for repeated subject-model runs on the same slice.
- Add `--scorer-runs N` or equivalent repeated scoring mode.
- Extend case metadata for bundle-based runs: each claim-slice case evaluator
  must declare `required_reference_files`, listing the relative reference paths
  expected to be available for that case. Mixed-stack cases must list multiple
  files.
- The runner must resolve prompt material from the bundle snapshot, not the live
  repo. At minimum, it must load the bundle `SKILL.md` and record which bundle
  reference files were attached for the case based on the checked-in metadata.
- Write machine-readable summary output including per-case and per-dimension
  scores (`first_shot_resolution`, `root_cause_accuracy`, `fix_accuracy`,
  `verification_quality`, `evidence_discipline`), mean, median, standard
  deviation, pass count, partial count, fail count, and
  `confident_wrong_answer` count.
- Archive raw subject responses and raw scorer JSON for every case, run, and
  scorer pass. Summary-only output is not sufficient for claim mode.
- Emit a provenance file for each run set that records:
  - bundle manifest path / snapshot id
  - case manifest path
  - subject model
  - scoring model
  - CLI arguments
  - timestamp
- Add a comparison report that takes baseline results and candidate results and
  emits the deltas required by D9.

Required frozen manifests:

- `benchmarks/slices/python-pipeline-core-14.txt`
- `benchmarks/slices/python-pipeline-claim-28.txt`
- `benchmarks/slices/no-regression-core.txt`

`no-regression-core.txt` must be a fixed, checked-in manifest. Do not allow
"representative subset" to remain informal.

### D9. Benchmark Protocol / Claim Gate

The upgrade must be measured as a before/after change in single-shot behavior,
not inferred from new files and case counts alone.

Required protocol:

1. After D6 core cases and D8.5 harness work are ready, freeze a **baseline
   skill bundle snapshot** of the current skill before any D1-D5 behavior
   changes are landed. This includes D3/D4 edits to already-routed reference
   files.
2. Run the target model on `benchmarks/slices/python-pipeline-core-14.txt`
   using that baseline snapshot bundle and record:
   - exact bundle snapshot id / manifest path
   - source commit
   - source kind (`repo`, `archive`, or `installed`)
   - subject model
   - scoring model
   - run count
   - scorer run count
3. Record:
   - `first_shot_resolution`
   - `root_cause_accuracy`
   - `fix_accuracy`
   - `verification_quality`
   - `evidence_discipline`
   - count of `confident_wrong_answer`
   - score variance across repeated runs
4. Implement D1-D5, D6.5, D6.6, D7, and D8.
5. Create a candidate skill bundle snapshot from the upgraded skill and re-run
   the same 14-case slice against that candidate bundle.
6. Run a no-regression pass on the fixed manifest
   `benchmarks/slices/no-regression-core.txt`.
7. After D6.5 stretch cases exist, run the expanded
   `benchmarks/slices/python-pipeline-claim-28.txt` slice before making any
   `90%` single-shot claim. That manifest may contain only cases with
   `one_shot_eligible: true`; any timing case included must be explicitly marked
   `determinism: controlled` with assets proving the controlled amplifier.
8. Claim-mode runs must use repetition:
   - at least `3` subject-model runs on the same slice
   - at least `2` scorer passes per response, or an equivalent adjudication rule
   - aggregate with median case score and report spread
9. If the claim threshold is met in only one noisy run but not the repeated
   aggregate, the claim fails.
10. Claim-mode outputs must be auditable:
    - raw subject responses archived for every case/run
    - raw scorer JSON archived for every scorer pass
    - provenance manifest archived with the bundle snapshot id and case manifest
    - baseline-vs-candidate diff report archived alongside summaries

The previous single-run protocol is not sufficient for a public `90%` number.

Acceptance tiers:

- **Material improvement**
  - `first_shot_resolution` improves by at least 8 points on the 14-case stack slice
  - `root_cause_accuracy` improves by at least 5 points
  - `confident_wrong_answer` count does not increase
  - no more than 3-point regression on the fixed no-regression slice

- **Strong upgrade**
  - at least 85 `first_shot_resolution` on the 14-case stack slice
  - at least 85 `root_cause_accuracy`
  - at least 80 `fix_accuracy`
  - no catastrophic regression on the fixed no-regression slice

- **Allowed to claim `90%` single-shot for this stack family**
  - at least 90 `first_shot_resolution` on the expanded 28-case claim manifest
  - at least 90 `root_cause_accuracy`
  - at least 85 `fix_accuracy`
  - `confident_wrong_answer` rate not worse than baseline
  - no more than 2-point regression on the fixed no-regression slice
  - mixed-stack routing validated: the upgraded skill actually loads the new
    references through Phase 2A and Phase 4
  - every claim-manifest case is `one_shot_eligible: true` and asset-backed
  - the repeated-run aggregate meets threshold, not just a single lucky run

Do not use the `90%` claim if only the 14 core cases exist.
Do not use the `90%` claim if the harness cannot reproduce baseline vs
candidate results from checked-in manifests and archived raw outputs.
Do not use the `90%` claim if claim-mode runs are not executed against a frozen
skill bundle snapshot.

### D9.5. Generalization Guardrail For Reference Docs

To prevent overfitting the shared skill to `tenderpdf`, every new reference file
must follow this writing rule:

- Name the pattern as a transferable root-cause class first.
- Put tender-specific framework details (`__reactProps`, Radix, Rich+devnull,
  etc.) in examples or proof notes, not in the abstract definition alone.
- At least one pattern per new file should include a non-tender-specific example
  or alternate formulation to prove it generalizes.

---

## Implementation Order

| Step | Deliverable | Depends On | Parallelizable |
|---|---|---|---|
| 0 | Evidence appendix + source mapping | None | Yes |
| 1 | D6: Benchmark cases SA-001..006, LP-001..004, TU-001..004 | 0 | No — sequential |
| 2 | D8.5: Improve benchmark harness + add bundle/slice infrastructure | 1 | No — sequential |
| 3 | D9 baseline run on pre-upgrade skill bundle snapshot using the fixed 14-case slice | 1, 2 | No — sequential |
| 4 | D1: `scraping-automation-patterns.md` | 0, 3 | Yes — with 5, 6, 7 |
| 5 | D1.5: `terminal-ui-patterns.md` | 0, 3 | Yes — with 4, 6, 7 |
| 6 | D2: `llm-pipeline-patterns.md` | 0, 3 | Yes — with 4, 5, 7 |
| 7 | D3 + D4: Update `bug-patterns.md` + `backend-patterns.md` | 0, 3 | Yes — with 4, 5, 6 |
| 8 | D5: Update `SKILL.md` (Phase 2 + Phase 4 + triggers + stack-scoped 0.5) | 4, 5, 6, 7 | No — sequential |
| 9 | D6.5 + D6.6: Stretch cases, claim eligibility metadata, and required assets | 1, 3 | Yes |
| 10 | D7 + D8: Update `COVERAGE_MATRIX.md` + `index.yaml` | 1, 9 | No — sequential |
| 11 | Post-upgrade candidate bundle snapshot + 14-case rerun + fixed no-regression gate | 2, 3, 8, 10 | No — sequential |
| 12 | Expanded 28-case claim-gate benchmark run (bundle mode, repeated-run, auditable artifacts) | 9, 11 | No — sequential |

Steps 1-3 establish the clean measurement baseline and must happen before
behavior-changing skill/reference edits land.
Steps 4-7 are independent content work and should be parallelized.
Steps 8-12 are sequential because the public claim depends on measured
before/after bundle results.

---

## Success Criteria

- All patterns have: symptom, why, prove, fix — sourced from real git history and code
- D1.5 terminal-ui-patterns.md covers the 8 patterns from 13 Rich/Live commits
- D2 correctly reframes tier tracking as "buried in DEBUG" not "missing"
- D3 error suppression pattern includes decision tree (intentional vs accidental)
- SKILL.md Phase 2A and Phase 4 both route/load all 3 new reference files
- Mixed-stack co-loading rules exist for scraping + backend, LLM + backend/external intelligence, and terminal UI + timing
- Phase 0.5 is explicitly stack-scoped, internal-only, and does not assign verdict confidence
- 14 benchmark cases pass CASE_TEMPLATE format validation
- Stretch cases expand the target stack slice to 28 total cases: 12 scraping, 8 LLM pipeline, 8 terminal UI
- Every claim-manifest case includes assets/, and the full 28-case public claim slice is 100% asset-backed
- Every public claim-manifest case is marked `one_shot_eligible: true`; any timing-sensitive case included is marked `determinism: controlled` with explicit amplifier evidence
- Every claim-slice evaluator declares `required_reference_files` so bundle-based runs can prove which routed references were attached
- Coverage matrix accounts for 3 new domains
- index.yaml updated with correct case counts for the fully authored target slice
- Benchmark harness supports bundle-based runs (`--skill-bundle`), fixed case manifests, repeated runs, and non-overwriting result sets
- Bundle snapshots have a documented structure, can be created from repo staging or the built `.skill` archive, and do not require breaking changes to install/update layout
- Baseline, candidate, and diff reports are reproducible from checked-in manifests and archived raw outputs
- Baseline bundle snapshot is captured before D1-D5 behavior changes land
- Baseline and post-upgrade benchmark results are recorded for the 14-case slice
- Claim-mode runs archive raw subject responses, raw scorer JSON, provenance manifests, and bundle snapshot metadata
- No increase in confident-wrong answers on the target stack slice
- No existing patterns or benchmark cases broken
- `90%` single-shot claim is used only if D9 claim-gate thresholds pass on the expanded 28-case slice
- New reference files are written as transferable bug classes, not tender-only playbooks

## Out of Scope

- Changes to tender_scraper.py or tender_analyzer.py (project files)
- New features in the tender pipeline
- Changes to non-relevant reference files (java-patterns, windows-packaging, etc.)
