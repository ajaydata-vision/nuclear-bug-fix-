---
name: nuclear-bug-fix
metadata:
  version: "1.15"
  source_commit: "9172d29cd1d1b6839171c8d4456761ce39383a9f"
  repo: https://github.com/ajaydata-vision/nuclear-bug-fix-
description: >
  Most powerful bug-fixing skill for bugs surviving code review, careful
  planning, and multiple fix attempts. Triggers on ANY stack, ANY language,
  ANY framework. Use when user says "still broken", "tried everything",
  "code review didn't help", "nothing works", "find the bug", "help me debug",
  "bug not resolved", or describes a silent failure. Also triggers for: UI
  rendering wrong, component not updating, CSS broken in prod, hydration
  mismatch, bundle error, CORS failure, WebSocket not connecting, API returns
  success but state not updated, DB write returns stale data, auth token
  rejected, background job silently failing, queue message not consumed,
  webhook not firing, microservice not responding, pipeline failing, data
  transform wrong, ETL dropping rows, CI/CD deploy succeeds but app broken,
  works locally but fails in prod, intermittent crashes, race conditions,
  bug came back after fix, any bug already looked at once.
  ALWAYS use this skill instead of a generic debugging response.
---

# ☢️ Nuclear Bug Fix

---

## UPDATE COMMAND — `/nuclear-bug-fix update`

If the user invokes this skill with the argument `update`
(i.e. types `/nuclear-bug-fix update`), do NOT run the bug-fix methodology.
Instead, run the update check:

```
STEP 1: Locate the update script (check both install locations)
  Bash / Git Bash / WSL:
    Personal install:  bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh
    Project install:   bash .claude/skills/nuclear-bug-fix/scripts/update.sh

  Windows PowerShell:
    Personal install:  & "$HOME\.claude\skills\nuclear-bug-fix\scripts\update.ps1"
    Project install:   & ".\.claude\skills\nuclear-bug-fix\scripts\update.ps1"

  Use the script that matches the current shell.
  Try personal first. If the file does not exist, try project.
  If neither exists: the skill was not installed from a directory; use manual reinstall.

STEP 2: Report what happened
  - If already up to date:  "nuclear-bug-fix is current (version: <version>)"
  - If updated:             Report the updater output directly, including the full diff URL when shown.
  - If error:               Show the error and the reinstall commands:
                            macOS/Linux:  curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.sh | bash
                            Windows PS:   irm https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.ps1 | iex

The update script handles everything. Just run it and report the output.
Do not proceed to the bug-fix methodology when the argument is "update".
```

---

## SKILL DISCLOSURE

When you apply this skill, state one short line near the start of the response:

`Using skill: nuclear-bug-fix`

If you are only partially applying it, say:

`Applying nuclear-bug-fix methodology`

If multiple skills are being used, list them briefly on one line.
Do not repeat the disclosure line multiple times in the same response.

If the user asks how the diagnosis or fix was found, explicitly say it was
found by applying the `nuclear-bug-fix` skill or methodology.

---

You are an **adversarial senior engineer**. Your only job is to find
and fix the bug. Not to be polite. Not to suggest alternatives. To be RIGHT.

This skill works on ANY technology — backend, frontend, mobile, infra,
automation, database, API, CLI, embedded. Stack does not matter.
The methodology is universal.

---

## PHASE 0 — REPRODUCE FIRST (Before Everything Else)

**You cannot debug what you cannot reproduce. This is non-negotiable.**

Debugging is an art only when you can't reproduce the bug. Until you can make it fail on demand, you are guessing — not debugging.

```
Step 1: Can you make it fail RIGHT NOW, on demand?
  YES → You have a Bohrbug. Complete Steps 2–4 below, then go to Phase 1.
  NO  → This is a Heisenbug, Mandelbug, or one-time event.
        Complete Steps 2–4 below, then go to Phase 1 (still collect all
        intake context — stack, versions, symptoms, existing logs).
        After intake, go to Phase 2 (start from 2A).
        Phase 2D will classify the bug type after 2A/2B/2C routing runs.

  FRONTEND BUG + chrome-devtools-mcp configured?
  → Reproduce directly: navigate to the page, trigger the action, observe
    DOM state, console errors, and network requests in the live browser.
    Do not ask the user to describe it — see it yourself.

Step 2: Stimulate — do NOT simulate.
  STIMULATE = Use the real environment, real data, real conditions.
              Reproduce in staging that mirrors prod exactly.
  SIMULATE  = Use mocks, stubs, fake data, simplified conditions.
              This is DANGEROUS. A simulated failure is not the real bug.
              The fix will not work in production.

Step 3: Find the exact conditions.
  What input? What user? What load? What time? What sequence of actions?
  The more specific the reproduction steps, the faster the fix.
  Vague repro = vague fix = doesn't hold in production.

Step 4: Preserve evidence IMMEDIATELY.
  Before touching anything:
  □ Export logs NOW (containers recycle, logs rotate, auto-scaling destroys evidence)
  □ Capture metrics/traces for the failure window
  □ Take screenshots/recordings of the failure
  □ Export DB state if relevant
  □ Note exact timestamp of failure
  Evidence lost = bug takes 10x longer to fix.
```

---

## PHASE 1 — INTAKE

Before diagnosing, collect context in ONE message.
Do not diagnose yet. Do not suggest anything yet.

Extract answers from the conversation first — only ask for what is missing.

```
1. SYMPTOM
   What happens vs what should happen?
   Paste the exact error message if there is one.
   If no error — describe what is missing or wrong in the output.

2. FAILURE POINT
   At which exact step does it break?
   What is the last thing that WORKS correctly?

3. RECENT CHANGES
   What changed right before this bug appeared?
   New deploy? Dependency update? Config change? Refactor?
   If it "always existed" — when was it first noticed?

4. CLOSED PATHS
   What have you already tried?
   What did code review find?
   What theories have been ruled out?
   These paths are CLOSED — I will not revisit them.

5. EXISTING LOGS / ERROR OUTPUT
   Paste any logs, stack traces, or error output you already have.
   Even if they seem unrelated — paste them.

6. THE CODE
   Paste the section closest to the failure point.
   Not the whole file. Just the broken area + the lines immediately before it.

7. STACK & EXACT VERSIONS (critical)
   Language + framework/library + infra/DB/platform.
   Include EXACT version numbers — not "latest" or "recent".
   Examples:
     Node.js 20.11.0 + Express 4.18.2 + Prisma 5.9.1 + PostgreSQL 16.1
     Python 3.11.4 + Django 4.2.8 + Celery 5.3.4 + Redis 7.2
     Java 17 + Spring Boot 3.2.1 + Hibernate 6.4.1 + MySQL 8.0.36
   Also: OS, deployment method (Docker/bare metal/serverless/k8s).
   Desktop / bridge / packaged apps must ALSO include runtime fingerprint:
     source vs frozen, onefile vs onedir, PyInstaller version, Python version,
     Node version, child-process command, current working directory, writable
     data path, whether stdout is a protocol/data channel, and where logs go.
   Required appendix for desktop / bridge / packaged apps:
     PyInstaller spec/build command, collected-data/hidden-import inputs,
     packaged helper/bundle manifest or extracted file tree, parent + child
     version stamp, transport framing contract, clean-machine vs dev-machine
     status, and one synchronized boundary timeline (spawn -> ready ->
     listener attach -> first event / failure).
   Version numbers are not optional — they unlock known-bug detection.

8. CONSISTENT OR INTERMITTENT?
   Does it always fail, or only sometimes?
   Under what exact conditions does it fail vs succeed?
   (load, input value, time of day, specific user, specific env)
```

---

## PHASE 2 — TRIAGE (Internal — Do Not Show to User)

Classify the bug before writing any diagnosis.
Pick the top 2 most likely categories before proceeding.

### 2A — Domain Classification (Route to Correct Reference File)

Identify the domain FIRST — determines which reference file to load.

| Domain | Signals | Reference File |
|---|---|---|
| **Frontend** | UI not rendering, CSS broken, component state wrong, hydration error, bundle error, browser-only bug, routing broken, form not submitting, WebSocket UI issue | `references/frontend-patterns.md` |
| **React Native** | Metro bundler error, module resolution failure, React Navigation params wrong/undefined, FlatList jank or blank items, Animated/Reanimated crash, Expo Go vs EAS build difference, AsyncStorage null on first launch, native module undefined in release, New Architecture (JSI/TurboModule) error, platform permission silent fail, iOS notch/safe area, deep link wrong screen, Fast Refresh stale state | `references/react-native-patterns.md` |
| **Mobile (generic)** | App crash, iOS/Android specific behavior (non-React-Native), push notification, offline sync, memory warning on device | `references/frontend-patterns.md` + mobile section |
| **Backend** | API response wrong, auth failing, DB issue, background job silent, queue not consumed, file upload broken, rate limit wrong, session bug, ORM query wrong | `references/backend-patterns.md` |
| **Python Desktop/UI** | PyQt6 widget update wrong, qasync slot never resumes, UI freezes during network/file/email action, QObject thread affinity error, app hangs on exit, desktop websocket/scheduler interaction broken | `references/python-desktop-patterns.md` |
| **Bridge / Adapter / Unofficial Client** | Python process talks to Node subprocess, stdout/stderr framed protocol, WhatsApp/Baileys bridge, websocket relay, scraper suddenly returns empty data, connected but no events, first event missing, duplicate event after reconnect | `references/bridge-adapter-patterns.md` |
| **Frozen / Packaged Runtime** | Works from source, fails in `.exe`; PyInstaller onefile/onedir bug; bundled data missing; hidden import missing; child process or asset not found; writable path differs from dev | `references/windows-packaging-patterns.md` |
| **Java Enterprise** | Users see each other's data, JSP shows stale content, NIO sends garbage or empty response, transaction didn't roll back, lazy loading exception, app hangs on shutdown, ClassCastException after WAR deploy, connection pool timeout, filter not applying, OutOfMemoryError in prod, Spring Security context empty, session has wrong values, @Transactional has no effect, @Async method running synchronously, @Scheduled never fires, Spring cache returning stale data, Kafka consumer not receiving messages, consumer rebalance storm, virtual thread throughput not improving, javax.* ClassNotFoundException after Spring Boot 3 upgrade | `references/java-patterns.md` |
| **PHP** | OPcache stale code after deploy, `==` vs `===` auth bypass, Eloquent N+1, queue job silent fail, `empty()` drops valid form value, PHP-FPM worker exhaustion, headers already sent, `session_start()` missing, composer autoload not regenerated, Laravel service container binding not found, Blade template cached with old output, CSRF 419 on form POST, transaction not committed on exception, persistent PDO connection leaks state, PHP CLI and FPM on different versions, `.env` not loaded in cron context, composer runtime version conflict | `references/php-patterns.md` |
| **Integration/Pipeline** | Webhook not firing, message queue dropped, microservice not responding, data transform wrong, ETL dropping rows, CI/CD broken, API gateway wrong, event not propagating | `references/integration-patterns.md` |
| **General/Cross-cutting** | Async/concurrency, environment mismatch, encoding, type bugs, caching, memory | `references/bug-patterns.md` |

**Immediately after identifying the domain — load the reference file and identify candidate patterns:**
```
PATTERN PRE-LOAD (run at Phase 2A, not Phase 4):
1. Load the reference file for the identified domain NOW.
2. Scan every pattern's Symptom heading.
3. Identify the 1–2 patterns whose Symptom most closely matches the intake description.
   Record as CP-1 (top candidate) and CP-2 (second candidate).
4. Read CP-1's Why section. This informs the entire Phase 3:
   - Phase 3.6: search for CP-1's specific error signatures and library names
   - Phase 3.7: surface the assumptions that CP-1's Why section identifies as risky
   - Phase 3.8: use CP-1's Prove as the primary forensic ask
   If CP-1's Prove output doesn't match → CP-2 becomes primary. Re-read its Why and Prove.
```
This pre-load is what converts Phase 3 from generic diagnosis to pattern-targeted single-shot.

Multiple domains? Load ALL relevant files. Frontend bug calling backend API = load both.
Desktop app spawning Node bridge from a packaged `.exe` usually means:
- load `references/python-desktop-patterns.md`
- load `references/bridge-adapter-patterns.md`
- load `references/windows-packaging-patterns.md`
- if timing-sensitive, also load `references/intermittent-race-bugs.md`

Bridge / Adapter / Unofficial Client subrouter:
- If the failure is spawn/handshake/listener/stdout framing/version-stamp/path related, treat it as local bridge / IPC first.
- If there was no local code/deploy/version change and raw upstream status/content changed, treat it as provider drift first and load `references/external-intelligence.md` before local bridge surgery.

### 2B — Boundary Ownership Matrix (Required For Desktop / Bridge / Frozen Bugs)

Before PH/CH elimination, name the first boundary that actually diverges.

| Boundary | What To Prove |
|---|---|
| UI loop | Event loop owner, blocking span, async-slot scheduling, task lifecycle |
| Worker thread | Thread name/ID, cross-thread widget/QObject mutation, queue handoff |
| Parent process | Spawn command, cwd, env, version stamp, resolved child path |
| Child bridge | Ready/auth state, listener graph, version stamp, runtime path |
| Transport | Framing contract, stdout/stderr ownership, sequence gaps, parse failures |
| Frozen bundle | `_MEIPASS`, collected files/plugins, writable data path, clean-machine behavior |
| Upstream provider | Raw status/body/signature, maintainer reports, provider drift evidence |

Record four facts:
- last known good boundary
- first bad boundary
- evidence required to prove it
- next boundary to test if disproved

### 2C — Symptom-to-Category Map

| Symptom Signal | Root Cause Category |
|---|---|
| Action fires, state not updated | Event system bypass / framework zone not notified |
| Resource found, interaction silently ignored | Interception layer (overlay, middleware, proxy, wrapper) |
| Works locally, fails in prod/staging | Environment mismatch (config, secrets, versions, timing) |
| Worked before, broken after change | Regression — recent change is the cause |
| Fails only sometimes / under load | Race condition / async gap / resource exhaustion |
| Write succeeds, read returns stale data | Caching / transaction isolation / wrong replica |
| API returns 2xx, nothing changes | Silent swallow / wrong endpoint / payload mismatch |
| Script runs, output is wrong | Format/type/encoding mismatch / off-by-one / wrong input file |
| Auth works, next call fails | Token/session expiry / scope / CORS / cookie domain |
| Works for some inputs, breaks for others | Edge case / null / empty / type coercion / locale |
| Crash only under load | Memory/connection exhaustion / deadlock / pool starvation |
| Deploy works, runtime fails | Missing env var / wrong path / permission / missing dep |
| Logs show nothing, bug is real | Log level too high / logs going to wrong sink / error swallowed |
| Fix applied, bug persists | Wrong code deployed / cache stale / fix in wrong branch |
| Bug fixed, different bug appeared | Fix introduced regression / two bugs masking each other |
| UI freezes while one action runs | Blocking I/O or CPU on UI/event-loop thread |
| Connected bridge, but first events missing or duplicated | Handshake/listener timing bug or listener leak |
| Works from source, fails in `.exe` | Frozen-runtime import/path/resource mismatch |
| Scraper suddenly returns empty data after site change | Upstream/provider drift or anti-bot behavior, not parser logic alone |

### 2D — Version Intelligence (Run After Domain Classification)

Extract exact versions from intake. Then run this check:

**Step 1 — Flag version risk:**
```
Is the user on:
- A version < 6 months old?      → Possible unpatched bug. Search release notes.
- A version > 2 years old?       → Missing critical patches. Check CVEs.
- A version that was just updated → Regression. Search changelog for breaking changes.
- Mismatched peer dependencies?   → Compatibility issue. Check compatibility matrix.
- A known-problematic version?    → Search "[library] [version] bug" before diagnosing.
```

**Step 2 — Version mismatch detection:**
Check if the versions reported are compatible with each other.
Known danger combinations:
- ORM version ahead of DB driver version
- Framework version incompatible with its plugin/extension version
- Runtime version incompatible with native module
- Node/Python/Java version below framework's minimum requirement
- GUI framework version incompatible with event-loop adapter
- Parent app protocol version incompatible with child bridge version
- PyInstaller mode incompatible with runtime path assumptions

**Step 3 — Trigger external search if:**
- Error message contains a library name + version number
- Bug started after a dependency update
- Behavior contradicts what the official docs say it should do
- Bug involves a protocol (HTTP/2, WebSocket, SMTP, OAuth) → check RFC
- Bug is security/auth related → check CVEs
→ Go to Phase 3.6 (External Intelligence) immediately

### 2E — Bug Classification (Critical — Determines Entire Strategy)

Different bug types require completely different debugging strategies.

```
BOHRBUG  — Deterministic. Reproducible. Same input → same failure.
           Strategy: Standard. Use Phases 3–6 as written.
           Sign: "It always fails when I do X"

HEISENBUG — Disappears or changes when observed/debugged.
            Cause: Race condition, timing, debugger alters execution,
                   uninitialized variable, optimizer changes behavior.
            Strategy: In Phase 4, load references/intermittent-race-bugs.md.
              No breakpoints. Find the uncontrolled variable.
              Amplify race window. Non-invasive logging. TSan.
            Sign: "It disappears when I try to debug it"

MANDELBUG — Chaotic. Fixing one reveals two more bugs.
            Cause: System grown without design. No clear ownership.
            Strategy: STOP patching symptoms. Draw the full dependency
              graph. Find which layer owns ambiguous state. Fix there.
              A workaround may be more appropriate than a deep fix.
            Sign: "Every fix makes it worse or reveals new bugs"

SCHROEDINBUG — Worked until someone read the code and saw it shouldn't.
               Cause: Lucky undefined behavior. Accidental correctness.
               Strategy: Code IS wrong. Rewrite from first principles.
                         Do NOT preserve old behavior.
               Sign: "I realized this code can't possibly work"
```

### 2F — Contributing Factor Analysis

The median production incident involves 3.5 contributing factors.
Incidents with 5+ contributing factors take 3x longer to resolve.

```
Single factor:  One line is wrong. Standard Phase 3.
Multi-factor:   Multiple conditions must align to trigger the bug.
                Map ALL contributing factors before fixing any one.
                Fixing factor 1 alone will not fix the bug.
```

### 2G — Meta-Checks (Always Run Before Diagnosis)

Before diagnosing the code, verify the debugging setup itself is not lying:

1. **Is the code you edited actually the code being executed?**
   - Compiled language → was it recompiled?
   - Docker → was container rebuilt and restarted?
   - Cached build → was cache cleared?
   - Multiple instances → are all instances updated?
   - Wrong branch deployed?

2. **Are the logs you're reading actually from the failing execution?**
   - Log level set too high (INFO/WARN)? Error logged at DEBUG?
   - Logs going to different file/sink than you're reading?
   - Log statements actually reached? (not skipped by early return)
   - Buffered logs not flushed before crash?

3. **Is the test / reproduction case actually testing what you think?**
   - Test hitting a mock instead of real code?
   - Test data different from production data?
   - Test running in isolation but bug is about interaction?

4. **For desktop / frozen apps: are you debugging the same runtime shape that fails?**
   - Source run vs packaged `.exe`?
   - `onefile` vs `onedir`?
   - Same Python / Node / bridge build on both sides?
   - Same working directory, writable data directory, and plugin paths?

5. **For subprocess / bridge / adapter bugs: is the transport itself lying?**
   - Is stdout reserved for protocol frames, or polluted by logs?
   - Is the child process alive and on the expected version/build?
   - Did the handshake complete before the first event was emitted?
   - Are listeners registered once, or once per reconnect/restart?

6. **Is there more than one bug?**
   - First bug masking second bug?
   - Fix for Bug A revealing Bug B (which was always there)?

7. **Can you add logs / access the environment at all?**
   - If NO log access: rely primarily on external intelligence (Phase 3.6) and binary search (Phase 3.4). Still run the DDx Gate (3.9) — it operates on whatever evidence is available.
   - If NO code access: external intelligence becomes the primary diagnostic tool.

---

## PHASE 3 — ADVERSARIAL DIAGNOSIS

Execute steps in this order. Conditional steps are marked — skip them when their condition does not apply. All others are mandatory.

### 3.0 — CHECK THE PLUG (Obvious First)

Before any sophisticated diagnosis, check the embarrassingly obvious:
```
□ Is the service/server actually running?
□ Is it connected to the right database/network?
□ Are the credentials/secrets actually set?
□ Is the correct PORT open and reachable?
□ Is the correct ENVIRONMENT being targeted?
□ Has the code been DEPLOYED (not just committed)?
□ Has the process been RESTARTED after config changes?
□ Is there DISK SPACE available?
□ Is there enough MEMORY available?

These take 30 seconds to check.
Engineers waste 4 hours on sophisticated diagnosis before checking these.
```

### 3.1 — AUDIT TRAIL (Start Immediately — Never Skip)

Open a scratch file or notes doc RIGHT NOW. Record every step as you go.
Do not wait until later. Evidence from step 1 is already valuable at step 10.

```
Format for each entry:
[TIMESTAMP] HYPOTHESIS: [what you thought]
[TIMESTAMP] ACTION:     [what you did / changed / checked]
[TIMESTAMP] OBSERVED:   [what actually happened]
[TIMESTAMP] CONCLUDED:  [what this proves or eliminates]

Why this is non-negotiable:
1. You will circle back to dead paths after 3 hours without this
2. If someone else takes over, they start from the full picture
3. The pattern in failed attempts often points directly to root cause
4. It becomes the postmortem — don't write it twice
```

### 3.2 — ASSUME EVERYONE WAS WRONG

State: all prior assumptions are reset. Start from zero.

List **5–10 possible root causes** — including the embarrassing ones:
- Wrong file / wrong instance / wrong environment being used
- Code change not deployed — old version still running
- Caching at ANY layer (in-memory, HTTP, CDN, DB query cache, build cache)
- Encoding / charset / locale / timezone mismatch
- Type coercion (string vs int, null vs undefined vs 0 vs "")
- Off-by-one (index, page, offset, date boundary, fence-post)
- Async gap — result consumed before operation completes
- Event/signal not reaching the actual handler
- Interception layer absorbing the action (proxy, middleware, wrapper)
- Correct logic, wrong data flowing in from upstream
- Error caught and swallowed silently in a try/catch somewhere
- Two bugs interacting — fixing one reveals the other

### 3.3 — LAST KNOWN GOOD ANALYSIS *(run only if this is a regression)*

Skip this step if the bug is new — i.e. there was never a working version.
Run this step if it worked before and now it doesn't.

If the bug is a regression (worked before, broken now):

- What EXACTLY changed between last working state and now?
- If code change: diff the relevant files. What lines changed?
- If dependency update: which version introduced it? (`git bisect` / changelog)
- If data change: what data exists now that didn't before?
- If infra change: what is different about the environment?

The answer is always in the delta. Find the delta.

### 3.4 — BINARY SEARCH THE FAILURE

Systematically narrow the failure point. Do not guess.

```
Technique: Comment out / disable half the code path.
Does the bug still occur? → Bug is in the remaining half.
Repeat. Each iteration halves the search space.
Takes 5–7 steps to isolate ANY bug to a single line.
```

For data bugs:
```
Try with hardcoded known-good values at the failure point.
Does it work with hardcoded data? → Bug is in data pipeline upstream.
Does it still fail? → Bug is in the logic, not the data.
```

For network/API bugs:
```
Call the API directly (curl / Postman) bypassing your code.
Works directly? → Bug is in your code's request construction.
Fails directly? → Bug is in the API/server side.
```

### 3.5 — TRACE THE EXECUTION PATH

Walk the **exact execution path** from input/trigger to failure point.
Step by step. No summaries. No skipping. No "etc."

At each step state:
- What the code does
- What the system/runtime/framework expects to receive
- Where those two things might diverge

Pay special attention to:
- Every async boundary (await, callback, promise, goroutine, thread)
- Every type conversion (explicit or implicit)
- Every external system call (DB, API, filesystem, cache)
- Every condition branch (which path actually executes?)

### 3.6 — EXTERNAL INTELLIGENCE GATHERING

**Run this BEFORE writing forensic logs. Do not skip.**

The bug may already be documented, reported, fixed, or explained in official sources.
Searching takes 2 minutes. Rediscovering a known bug takes hours.

Load `references/external-intelligence.md` for the full source hierarchy and query strategy.

**Trigger web search when ANY of these are true:**
```
□ Error message is library-specific (contains framework/library name)
□ Behavior contradicts what official docs say should happen
□ Bug started after a version update
□ Bug involves a protocol (HTTP, WebSocket, OAuth, SMTP, gRPC, etc.)
□ Bug is auth/security related
□ Framework version is < 6 months old (possible unpatched bug)
□ You cannot explain WHY the code should fail based on reading it alone
□ The exact error message is cryptic or looks auto-generated by a library
□ Works from source but fails only in a packaged / frozen build
□ Stack uses an unofficial client, scraper, or provider bridge that may have upstream drift
□ Stack trace or error references: jboss, wildfly, weblogic, glassfish, payara,
  liberty, or any proprietary EE container class — search vendor docs first
□ Deployment descriptor is jboss-web.xml, weblogic.xml, glassfish-web.xml,
  or sun-web.xml — container-specific config; reference docs not a reference file
□ Reactive/WebFlux bug: use BlockHound to detect blocking calls on Reactor threads
  before diagnosing timeout or starvation symptoms
```

**Search priority order (always try in this sequence):**
```
1. Official docs for the exact API/method being used
   → Does the docs say it works differently from what the code assumes?

2. Changelog / release notes for the exact version in use
   → Is there a breaking change between the version that worked and current?

3. GitHub Issues for the library/framework
   → Search: "[library] [error message snippet] [version]"
   → Look for: open issues, closed issues with "won't fix", known workarounds

4. RFC / specification for the protocol involved
   → HTTP: RFC 9110, RFC 9112 | OAuth: RFC 6749, RFC 7636
   → WebSocket: RFC 6455 | JWT: RFC 7519 | SMTP: RFC 5321
   → Is the code implementing the spec correctly?

5. CVE database for security-related bugs
   → Search: "[library] [version] CVE"
   → Is this a known vulnerability with a patched version?

6. Package registry advisories
   → npm: npmjs.com/advisories | PyPI: pypi.org/project/[pkg]/#history
   → Maven: mvnrepository.com | Go: pkg.go.dev
   → Is this version flagged for security or compatibility issues?

7. MDN Web Docs / caniuse.com for browser APIs
   → Is the API supported in the browser where bug occurs?
   → Is there a known quirk in that browser's implementation?
```

**Search priority overrides for unstable desktop / bridge / packaged stacks:**
```
Unofficial client / scraper drift:
1. Repo issues / maintainer reports / provider-change evidence
2. Release notes / changelog for the scraper or client
3. Raw upstream response comparison
4. Only then local parser/business-logic diagnosis

Packaged runtime:
1. PyInstaller docs / hooks / collect-data guidance
2. PyInstaller issue tracker for the exact error
3. Framework-specific packaging notes (Qt/plugins, spawned helpers, cert/data paths)
4. Only then generic runtime docs

Bridge / child runtime / stdio protocol:
1. Library repo docs/issues for lifecycle and reconnect behavior
2. Transport framing contract and child_process / subprocess docs
3. Parent/child version and packaged-path evidence
4. Only then generic protocol RFCs
```

**What to do with search results:**
```
Found a matching known bug?
→ State it explicitly: "This is a confirmed bug in [library] [version]"
→ Provide the exact version that fixes it
→ Provide the workaround if fix version not available
→ Link to the issue/PR/changelog entry

Found a docs discrepancy?
→ The code is wrong vs the spec. Fix the code to match the docs.
→ Quote the relevant docs section in the verdict.

Found nothing?
→ This is a new/unknown bug. Continue to 3.7 (Find the Lies).
→ The forensic logging in 3.8 will prove the root cause.
```

### 3.7 — FIND THE LIES

List every assumption in the code that is **assumed true but never verified**.
These are the primary suspects.

Check every assumption in this list:

```
EXECUTION ASSUMPTIONS
□ Is this operation completing before the next line runs?
□ Is this branch actually being entered? (log the condition value)
□ Is this function actually being called? (log entry)
□ Is this the right function being called? (right instance/module)

DATA ASSUMPTIONS  
□ Is the value the expected TYPE? (not just visually similar)
□ Is the value the expected FORMAT? (date, number, string encoding)
□ Is the value non-null / non-empty / non-zero where assumed?
□ Is the value from the right source? (correct DB, correct API, correct file)

SYSTEM ASSUMPTIONS
□ Is the correct instance/connection/session being used?
□ Is the handler/listener/callback actually registered?
□ Is there an interception layer modifying/absorbing the action?
□ Is the state being mutated on the right object (not a copy)?
□ Is the error being caught and swallowed upstream?
□ Is the correct version of the module/file/dependency loaded?
□ Is the environment variable actually set in this runtime context?
□ Is the service/dependency actually running and reachable?
```

### 3.8 — FORENSIC LOGGING

**TARGETED PROVE FIRST — run this before any broad logging:**
If Phase 2A identified a domain with a dedicated reference file:
1. Load that reference file NOW (do not wait for Phase 4).
2. Find the pattern whose **Symptom** most closely matches the intake description.
3. Go directly to that pattern's **Prove** section.
4. Deliver that Prove as your first and primary forensic ask.
5. Output matches the Prove's described signature → strong evidence for that pattern.
   Proceed to 3.9. Do not add more logs unless the gate requires it.
6. Output is inconclusive or doesn't match → broaden to the full assumption list in 3.7.

Do NOT run the broad assumption-logging campaign when a reference pattern matches.
One targeted prove beats ten scattered logs. A 20-year architect adds one log, not fifteen.

Write debug logging code adapted to the user's actual stack.
Place a log at **every unchecked assumption** from 3.7 only when no reference pattern matches.
Make the bug prove itself. Never guess.

**Core logging principle:** Log type + value + identity, not just value.

```
# Type + value (adapt to language)
Python:       print(f"[DEBUG] {var=}, type={type(var).__name__}, repr={repr(var)}")
JavaScript:   console.log('[DEBUG]', {var, type: typeof var, value: JSON.stringify(var)})
Java (SLF4J+MDC — servlet-container safe, thread-aware):
              MDC.put("reqId", UUID.randomUUID().toString());
              log.debug("[DEBUG] var={} type={} threadId={}", var,
                        var != null ? var.getClass().getName() : "null",
                        Thread.currentThread().getId());
              // NIO: log.debug("[DEBUG] buf pos={} lim={} remaining={}", buf.position(), buf.limit(), buf.remaining());
              // Deadlock: long[] d = ManagementFactory.getThreadMXBean().findDeadlockedThreads(); log.debug("deadlocked={}", Arrays.toString(d));
Go:           log.Printf("[DEBUG] %T %+v", var, var)
```

```
# Desktop / qasync / packaged runtime fingerprint
import asyncio, logging, os, sys, threading
from pathlib import Path
log = logging.getLogger("nbf")
loop = asyncio.get_running_loop()
log.debug(
    "[DEBUG] pid=%s tid=%s thread=%s loopId=%s frozen=%s meipass=%s cwd=%s exe=%s argv=%s",
    os.getpid(),
    threading.get_ident(),
    threading.current_thread().name,
    hex(id(loop)),
    getattr(sys, "frozen", False),
    getattr(sys, "_MEIPASS", ""),
    os.getcwd(),
    sys.executable,
    sys.argv,
)
log.debug("[DEBUG] appdata=%s localappdata=%s home=%s", os.getenv("APPDATA"), os.getenv("LOCALAPPDATA"), str(Path.home()))
```

```
# Bridge / stdio protocol safety
# If stdout carries protocol frames, NEVER print logs there.
# Use stderr or a file sink only.
import logging, os, sys
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(message)s"))
bridge_log = logging.getLogger("bridge")
bridge_log.handlers = [handler]
bridge_log.setLevel(logging.DEBUG)
bridge_log.debug("bridge_seq=%s event=%s pid=%s child=%s", seq, event_name, os.getpid(), child_pid)
```

```
# Async timing (add to every async boundary)
log("[DEBUG] BEFORE async op, timestamp=" + now())
result = await asyncOp()
log("[DEBUG] AFTER async op, timestamp=" + now() + ", result=" + repr(result))
```

```
# Network/API (log full request AND full response)
log("[DEBUG] REQUEST: method=%s url=%s headers=%s body=%s" ...)
log("[DEBUG] RESPONSE: status=%s headers=%s body=%s time=%sms" ...)
```

```
# Database (log actual query + params + row count)
log("[DEBUG] QUERY: " + interpolated_query_with_values)
result = db.execute(query, params)
log("[DEBUG] ROWS RETURNED: " + len(result))
```

```
# File/Config (log absolute path + size + first bytes)
import os
log("[DEBUG] PATH RESOLVED: " + os.path.abspath(filepath))
log("[DEBUG] FILE SIZE: " + os.path.getsize(filepath))
```

```
# UI/Automation (log element state before every interaction)
log("[DEBUG] ELEMENT: tag=%s class=%s value=%s enabled=%s visible=%s" ...)
log("[DEBUG] ELEMENT AT CLICK COORDS: " + elementFromPoint(x,y).outerHTML)
screenshot("before_action.png")
```

```
# Deployed code verification (is your fix actually running?)
# Add a unique sentinel log line immediately after your fix
log("[DEBUG] ★★★ FIXED CODE EXECUTING v2 ★★★")
# If you don't see this in output → wrong code is running
# If stdout is the protocol channel, write the sentinel to stderr or a file.
```

**FRONTEND BUG + chrome-devtools-mcp configured?**
Skip manual log injection. Use MCP tools directly:
- Console errors → use the console messages tool
- Network request headers/response → use the network requests tool
- DOM state / computed styles → use evaluate JS or page source tool
- JS expression evaluation → use evaluate JS tool
These give the same evidence as forensic logs without modifying the code.

### 3.9 — DIFFERENTIAL DIAGNOSIS GATE (Mandatory Before Verdict)

> **Stuck before reaching this step?** If 2+ hours have passed with no clear hypothesis, jump directly to **3.13 — GET A FRESH VIEW** before running the gate.

**This gate exists to prevent the most common failure in debugging: issuing a verdict
that the evidence is consistent with, but does not uniquely prove.**

Consistency with evidence ≠ proof.
Evidence that supports your hypothesis but ALSO supports an alternative
does NOT eliminate that alternative. Only evidence that is INCONSISTENT
with an alternative eliminates it.

This gate forces you to find that eliminating evidence — or admit it doesn't exist yet.

**Load `references/ddx-gate.md` before executing this step.**

**FAST-PATH (use only when direct proof is unambiguous):**

If forensic logs show direct, unambiguous proof — exact line, exact value, exact
mechanism — AND no other explanation is logically possible, you may bypass the
full gate and issue a HIGH-confidence verdict directly.

Fast-path requires ALL of the following:
```
□ The log shows the exact failure mechanism (not just "consistent with" the failure)
□ The cause is deterministic — one cause, one effect, no timing dependency
□ The fix is precise and affects only the proven failure point
□ A reasonable engineer reading the log would have no alternative explanation
```

A reference file's pattern **Prove** log showing the exact signature described for that
pattern is strong targeted evidence: it was designed to surface the specific mechanism
of that pattern and to narrow the field significantly. If the Prove output matches the
described signature, it satisfies conditions 1 and 4 for well-discriminating patterns.
Apply the full sensitivity check (condition 2 and 3) before issuing HIGH confidence —
some Prove outputs narrow to one pattern; others narrow to two or three. State it as:
"Pattern proof: [pattern name] Prove log shows [exact output]. This matches the described
signature. Remaining alternatives eliminated / still possible: [state honestly]."

If ALL four are true → issue the verdict with HIGH confidence. State the proof
explicitly in the verdict as: "Direct proof: [log line / result that proves it]"

If ANY is uncertain → run the full gate (Steps 1–5 below).

---

**STEP 1 — GENERATE COMPETING HYPOTHESES**

List the 3 strongest alternative explanations for the same symptom.
Do NOT generate strawmen. These must be genuinely plausible.
Steelman each one — make the best possible case FOR it.

```
PRIMARY HYPOTHESIS (PH):
[The root cause you currently believe]

COMPETING HYPOTHESIS 1 (CH-1):
[The most plausible alternative — what a skeptic would say]

COMPETING HYPOTHESIS 2 (CH-2):
[Second most plausible alternative]

COMPETING HYPOTHESIS 3 (CH-3):
[Third most plausible alternative]
```

---

**STEP 2 — EVIDENCE MATRIX**

For each piece of evidence collected in 3.8, classify it:

```
| Evidence | Supports PH? | Consistent with CH-1? | Consistent with CH-2? | Consistent with CH-3? |
|---|---|---|---|---|
| [evidence 1] | YES/NO | YES/NO | YES/NO | YES/NO |
| [evidence 2] | YES/NO | YES/NO | YES/NO | YES/NO |
| [forensic log result] | YES/NO | YES/NO | YES/NO | YES/NO |

KEY INSIGHT:
Any row where CH-x = YES means that evidence does NOT eliminate CH-x.
You need a row where CH-x = NO to eliminate it.
Evidence that eliminates an alternative is called DIAGNOSTIC evidence.
Evidence that merely doesn't contradict is called CONSISTENT evidence.
Consistent evidence proves nothing. Only diagnostic evidence eliminates.
```

---

**STEP 3 — ELIMINATION ATTEMPTS**

For each competing hypothesis, answer these two questions:

```
CH-1: [name]
  STEELMAN: Why could this be right?
    [make the strongest possible case for CH-1]
  ELIMINATOR: What evidence would make CH-1 IMPOSSIBLE?
    [what would have to be true for CH-1 to be wrong?]
  DO WE HAVE THAT EVIDENCE?
    YES → CH-1 ELIMINATED. Evidence: [cite specific log/check/result]
    NO  → CH-1 STILL POSSIBLE → GO TO STEP 5 — Evidence Collection Plan

CH-2: [name]
  [same structure]

CH-3: [name]
  [same structure]
```

---

**STEP 4 — GATE CHECK AND CONFIDENCE SCORE**

```
GATE CHECKLIST:
□ PH is supported by DIRECT forensic proof (not just absence of alternatives)
□ CH-1 eliminated by specific evidence that is INCONSISTENT with CH-1
□ CH-2 eliminated by specific evidence that is INCONSISTENT with CH-2
□ CH-3 eliminated by specific evidence that is INCONSISTENT with CH-3

SENSITIVITY CHECK:
If the key evidence FOR the primary hypothesis turned out to be wrong:
  Would the verdict still hold? YES → High. NO → Medium.

CONFIDENCE SCORE:
  HIGH   (90-95%) → PH directly proven by forensic logs
                    AND all 3 CH eliminated by diagnostic evidence
                    AND sensitivity check passes

  MEDIUM (70-85%) → PH consistent with all evidence
                    AND alternatives eliminated mainly by absence
                    (no evidence FOR them, but no smoking-gun AGAINST either)
                    OR sensitivity check fails

  LOW    (50-65%) → PH plausible but competing hypothesis not eliminated
                    More evidence needed before issuing verdict

  BLOCK  (<50%)   → Evidence is ambiguous between two or more hypotheses
                    DO NOT issue verdict. Run Step 5 instead.

GATE STATUS:
  PASS (High or Medium) → Proceed to 3.10 VERDICT
  FAIL (Low or Block)   → Run Step 5 — collect eliminating evidence
```

---

**STEP 5 — EVIDENCE COLLECTION PLAN (If Gate Fails)**

If the gate fails, do not guess. Specify exactly what evidence would close it:

```
TO ELIMINATE CH-[x] I NEED TO OBSERVE:
  [exact log line / test result / check output that would make CH-x impossible]

HOW TO GET THAT EVIDENCE:
  [exact forensic log to add / test to run / check to perform]

EXPECTED RESULT IF PH IS CORRECT:
  [what the evidence will show if PH is true]

EXPECTED RESULT IF CH-x IS CORRECT:
  [what the evidence will show if CH-x is true instead]
```

This is not a dead end — it is a precise research plan.
Collect the evidence. Come back. Re-run the gate.

---

### 3.10 — VERDICT (Issued Only After DDx Gate Passes)

The verdict includes the gate's confidence score. It is non-negotiable.

```
GATE STATUS: [PASS — HIGH / PASS — MEDIUM]
CONFIDENCE:  [HIGH 90-95% / MEDIUM 70-85%]

ROOT CAUSE:
[One sentence. Specific. Stated as fact.]

WHY THIS HAPPENED:
[One sentence explaining the mechanism.]

ALTERNATIVES CONSIDERED AND ELIMINATED:
  CH-1 [name]: Eliminated because [specific evidence]
  CH-2 [name]: Eliminated because [specific evidence]
  CH-3 [name]: Eliminated because [specific evidence]

BEFORE:
[the broken code]

AFTER:
[the fixed code]

WHY THIS FIX WORKS:
[One sentence.]

IF CONFIDENCE IS MEDIUM — FLAG THIS:
  The verdict depends on [key evidence]. If that evidence turns out
  to be wrong, the most likely alternative would be [CH-x].
  Re-test under [condition] to confirm.
```



### 3.11 — 5 WHYS *(mandatory for bugs > 30 minutes; skip for trivial one-line fixes)*

The first answer is rarely the real root cause. It is a symptom.
Apply 5 Whys to find the systemic cause — the thing to fix so this class
of bug never recurs.

```
Format:
WHY 1: Why did the bug occur?
        → [immediate cause]
WHY 2: Why did [immediate cause] happen?
        → [deeper cause]
WHY 3: Why did [deeper cause] happen?
        → [deeper still]
WHY 4: Why did [deeper still] happen?
        → [systemic cause]
WHY 5: Why did [systemic cause] happen?
        → [ROOT CAUSE — usually a process, design, or knowledge failure]

Example:
WHY 1: Why did the date picker not set the date?
        → Selenium click fired but Angular didn't detect it
WHY 2: Why didn't Angular detect the click?
        → Native DOM event fired outside Angular's NgZone
WHY 3: Why was a native DOM event used?
        → Developer assumed .click() works with all frameworks
WHY 4: Why did developer assume this?
        → No team documentation on framework-specific automation
WHY 5: Why is there no documentation?
        → ROOT CAUSE: No onboarding guide for automation testing
                      standards across the team

The Phase 3.10 verdict fixes the symptom (wrong click method).
The 5 Whys root cause identifies what to fix so it never happens again.
BOTH fixes should be provided.
```

### 3.12 — CHANGE ONE THING AT A TIME *(apply when implementing any fix at 3.10 or during Phase 6 escalation)*

When applying fixes — especially during escalation:
```
NEVER change two things simultaneously.
If the bug disappears, you won't know which change fixed it.
If the bug changes behavior, you won't know what caused the change.

Protocol:
1. Apply ONE change
2. Test under EXACT reproduction conditions from Phase 0
3. Document result (fixed / not fixed / changed behavior)
4. If not fixed: REVERT that change completely
5. Apply NEXT change
6. Repeat

This is the only way to isolate what actually fixed it.
This is also how you avoid: "it's fixed" → bug returns in 2 days.
```

### 3.13 — GET A FRESH VIEW (If Stuck > 2 Hours)

If 2+ hours have passed with no resolution, stop and reset:

```
RUBBER DUCK: Explain the bug out loud — step by step, to anyone or anything.
  As you articulate it precisely, the flaw often surfaces.
  The act of explaining forces you to state every assumption explicitly.
  "It should work because..." — that sentence contains the bug.

PAIR DEBUG: Hand the audit trail to another engineer cold.
  Brief them only on the symptom. Let them read the trail.
  Fresh eyes see what familiarity hides.
  Junior engineers find what seniors miss — no inherited assumptions.

STEP AWAY: Sleep on it if not urgent. The unconscious brain debugs.
  The "shower fix" is a real phenomenon. Forced rest often breaks the logjam.

FLIP YOUR ASSUMPTION: If you're convinced the bug is in Module A →
  Deliberately investigate Module B.
  The real issue is often in the last place you'd look.
  If everyone agrees it's the database → check the application layer.
```

---

## PHASE 4 — DEEP PATTERN REFERENCE (Domain Router)

The reference file was already loaded at Phase 2A. This phase is for **comprehensive review** — re-read it fully to catch any patterns the targeted Prove in Phase 3.8 may have missed, or to confirm the Prove result maps to exactly one pattern.

If the Phase 3.8 Prove matched cleanly → use Phase 4 to verify no alternative pattern in the same file produces an identical Prove output (sanity check before verdict).
If the Phase 3.8 Prove was inconclusive → scan all patterns in the file now to find the next best candidate.

| File | When to Load | Contents |
|---|---|---|
| `references/react-native-patterns.md` | Any React Native bug: Metro bundler, React Navigation, FlatList/lists, Animated/Reanimated, Expo/EAS, AsyncStorage, native modules, New Architecture (JSI), platform permissions, Hermes, Fast Refresh | Metro cache, navigation stack, list rendering, worklet crashes, build environment, state/storage, native linking, debug interference |
| `references/frontend-patterns.md` | Any UI/browser/CSS/bundle/routing bug, generic mobile (non-RN) | Rendering, hydration, state, CSS, forms, WebSocket, browser compat, performance |
| `references/backend-patterns.md` | Any API/auth/DB/queue/job/session bug | REST/GraphQL, auth, ORM, background jobs, file upload, rate limiting, sessions |
| `references/python-desktop-patterns.md` | PyQt6/qasync/UI-thread-affinity/desktop scheduler or websocket bugs | Loop ownership, async slots, UI freezes, shutdown cleanup, desktop SQLite usage |
| `references/bridge-adapter-patterns.md` | Python<->Node bridges, stdout-framed protocols, reconnect/listener bugs, unofficial client/scraper drift | IPC lifecycle, framing discipline, reconnect ordering, provider drift handling |
| `references/windows-packaging-patterns.md` | Works from source but fails when frozen / packaged | PyInstaller layout, `_MEIPASS`, hidden imports, Qt plugins, writable paths, bundled helpers |
| `references/integration-patterns.md` | Any webhook/queue/pipeline/microservice bug | Webhooks, message queues, event-driven, ETL, CI/CD, API gateway, service mesh |
| `references/bug-patterns.md` | Async, environment, encoding, type, memory, concurrency | 10 categories, 45 universal patterns |
| `references/intermittent-race-bugs.md` | ANY intermittent failure, Heisenbug, race condition, flaky test, "only sometimes", "only under load" | Signature hunting, race window amplification, non-invasive logging, TSan tools, 8 race types with prove+fix, Fix Ladder, verification |
| `references/world-methods.md` | Mandelbug (chaotic, every fix reveals more bugs), multi-factor incident (3+ contributing factors), bug unsolved after 2+ hours | Agans' 9 Rules, bug taxonomy, 5 Whys deep-dive, Fishbone/Ishikawa, Fault Tree Analysis, Google SRE postmortem, Chaos Engineering |
| `references/ddx-gate.md` | Always — load before executing step 3.9 | ACH methodology, evidence matrix, cognitive bias catalog, common false diagnoses, confidence calibration |
| `references/external-intelligence.md` | Version mismatch, library-specific error, protocol bug, CVE suspected | RFC lookup, changelog analysis, GitHub issues, CVE database, MDN/caniuse |

Each reference file has: symptom → why → how to prove → how to fix.
Load them. Read them. Match the pattern. Do not guess.

Co-loading rules for this stack family:
- Desktop + Bridge: load `references/python-desktop-patterns.md` and `references/bridge-adapter-patterns.md`
- Bridge + Frozen: load `references/bridge-adapter-patterns.md` and `references/windows-packaging-patterns.md`
- Desktop + Bridge + Frozen: load all three, plus `references/intermittent-race-bugs.md` if timing-sensitive
- Provider drift with no local change: load `references/bridge-adapter-patterns.md` and `references/external-intelligence.md` before local IPC/path debugging

---

## PHASE 5 — VERIFY

After applying the fix, give the user an explicit verification checklist:

```
VERIFICATION CHECKLIST

1. CONFIRM RIGHT CODE IS RUNNING
   □ Recompile / rebuild / restart / clear cache as needed
   □ Look for sentinel log: "[DEBUG] ★★★ FIXED CODE EXECUTING ★★★"

2. CONFIRM BUG IS GONE
   □ [specific thing to run or check]
   □ Expected output: [exact value/behavior]

3. CONFIRM NO REGRESSION
   □ Test the happy path
   □ Test with: null input, empty input, max value, min value
   □ Test the exact scenario that was broken before

4. BLAMELESS MICRO-POSTMORTEM (for any bug that took > 1 hour)
   □ What was the root cause? (from 5 Whys)
   □ What could have caught this earlier?
   □ What will prevent this class of bug permanently?
   □ What test should be added to the regression suite?
   Document this. Don't skip it. It's how the team gets smarter.

5. FRONTEND BUG + chrome-devtools-mcp configured?
   □ Navigate to the fixed page in the live browser
   □ Trigger the exact failing scenario from Phase 0
   □ Confirm: no console errors, network requests correct, DOM state correct
   □ This replaces manual DevTools steps — verify directly, do not describe.
```

---

## PHASE 6 — ESCALATION LOOP (If Bug Persists After Fix)

If the fix did not resolve the bug, do NOT give up. Execute this loop:

### Step 1 — Verify the fix actually ran
```
Is the sentinel log line appearing?
NO → Code not deployed. Fix the deployment. Not a logic bug.
YES → Continue to Step 2.
```

### Step 2 — Verify the fix addressed the right line
```
Is the BEFORE code actually what was in the file?
Run git diff or compare carefully.
Mismatch → You fixed the wrong line. Re-read 3.7.
```

### Step 3 — Check for a second bug, or revisit the DDx Gate
```
CASE A: First bug is fixed. New symptom is different from original.
  → Two bugs were present. First fix revealed the second.
  → Run Phase 3 again from scratch on the NEW symptom.

CASE B: Same symptom persists. Verdict was MEDIUM confidence.
  → Return to the DDx Gate (3.9). The uneliminated competing
    hypothesis is now the primary suspect.
  → Collect the evidence specified in DDx Gate Step 5 (Evidence Collection Plan).
  → Re-run the gate with the new evidence.
  → Issue a new verdict if the gate passes.
```

### Step 4 — Escalate to minimal reproduction
```
Strip everything. Create the smallest possible failing case:
- Remove all unrelated code
- Use hardcoded inputs
- Run in isolation (no DB, no network, no framework if possible)

If it still fails in isolation → core logic bug. Reread 3.5-3.8.
If it passes in isolation → bug is in the interaction, not the logic.
  → Add back one layer at a time until it breaks again.
  → The layer that breaks it = the culprit.
```

### Step 5 — Flip the debugging direction
```
Instead of tracing forward from the input:
Trace BACKWARD from the failure point.
At the point of failure, what VALUE would have caused this?
Work backward through the code to find where that value came from.
```

### Step 6 — External intelligence on the specific failure
```
If all internal analysis is exhausted:
Search for the EXACT symptom + EXACT version + EXACT stack online.

Queries to try:
  "[framework] [version] [error message]"
  "[library] [version] github issue"
  "[framework] [version] breaking change [feature]"
  "[protocol] RFC [behavior] compliance"

Check:
  - GitHub Issues (open AND closed)
  - Official changelog between working version and current
  - Stack Overflow with exact error text in quotes
  - Framework's official migration guide if version changed

This is the last resort. If a match is found here →
state it as a confirmed known bug with source link.
```

---

## IRONCLAD RULES

**Before diagnosis:**
1. **Reproduce first.** You cannot debug what you cannot reproduce. No repro = no fix.
2. **Stimulate, never simulate.** Real environment, real data, real conditions. Always.
3. **Preserve evidence immediately.** Logs, metrics, DB state before they're lost.
4. **Classify the bug type.** Bohrbug, Heisenbug, Mandelbug, Schroedinbug. Each needs a different strategy.
5. **Check the plug first.** 30 seconds on obvious checks before 4 hours of sophisticated analysis.
6. **Start the audit trail.** Open a scratch doc. Record every step from this moment.

**During diagnosis:**
7. **Never assume.** Every assumption gets a log or assertion.
8. **Meta-check first.** Verify the debugging setup before the code.
9. **Search before concluding.** Phase 3.6 runs before forensic logs. Known bug = known fix.
10. **Exact versions required.** They unlock known-bug detection.
11. **Docs trump assumptions.** Official docs say it works differently → code is wrong.
12. **RFC is ground truth for protocols.** HTTP, OAuth, JWT, WebSocket, SMTP checked against spec.
13. **Mandelbug? Stop patching.** Map the full dependency graph. Find which layer owns ambiguous state. Fix the architecture, not the symptom.

**For intermittent / race bugs:**
14. **Intermittent = uncontrolled variable.** It is NOT random. Find the variable that determines whether it fires.
15. **Never breakpoint a Heisenbug.** Breakpoints change timing and make the race disappear. Use nanosecond-timestamp logging and operation IDs only.
16. **Amplify before diagnosing.** Add artificial sleep at the suspected race window. Fires consistently → window confirmed. Remove sleep, fix synchronization.
17. **Run TSan first.** Go: -race, C/C++: -fsanitize=thread, Java: JCStress. Finds in one run what humans miss in days.

**Before issuing the verdict:**
18. **Run the DDx Gate. Always.** A verdict without the gate is a guess wearing a suit. Fast-path (direct unambiguous proof) still counts as running the gate — see 3.9 for criteria.
19. **Consistency ≠ proof.** Evidence consistent with your hypothesis but also consistent with an alternative eliminates nothing. Only INCONSISTENT evidence eliminates.
20. **Steelman every alternative.** Make the best possible case FOR each competing hypothesis. Weak strawmen produce false confidence.
21. **Gate failure = evidence collection plan.** Specify exactly what log/test/check would close it. Not a new guess — a precise research plan.
22. **One verdict, confidence-scored.** Not a hedge list. Commit. But state the confidence level honestly.

**After the fix:**
23. **Fix only what is broken.** Never rewrite the whole file.
24. **Always BEFORE / AFTER.** Never just the new code alone.
25. **Sentinel log in every fix.** Confirm the fix is actually running.
26. **Change one thing at a time.** Two changes = you don't know what fixed it.
27. **If you didn't fix it, it ain't fixed.** Must fail under old conditions. Must pass after fix. Same conditions.
28. **Apply 5 Whys after verdict.** *(skip for trivial one-line fixes)* The first answer is a symptom. The 5th Why is the root cause.
29. **Write the micro-postmortem.** Every bug > 1 hour: root cause, what caught it, what prevents recurrence.

**If the fix fails:**
30. **Fix didn't work?** Run Phase 6. Do not repeat Phase 3 with the same assumptions.
31. **Medium confidence verdict failed?** The DDx Gate's uneliminated CH is the next suspect. Investigate it next.
32. **Multi-factor incident?** Map ALL contributing factors before fixing any one.
33. **Silent failure?** Find the swallow. Something is catching and dropping the error.
34. **Works locally, fails in prod?** Always environment: config, secrets, version, load, timing.
35. **Never revisit closed paths.** Already tried = dead path. Move on.
