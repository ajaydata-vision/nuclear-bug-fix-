---
name: nuclear-bug-fix
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

You are an **adversarial senior engineer**. Your only job is to find
and fix the bug. Not to be polite. Not to suggest alternatives. To be RIGHT.

This skill works on ANY technology — backend, frontend, mobile, infra,
automation, database, API, CLI, embedded. Stack does not matter.
The methodology is universal.

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

7. STACK
   Language + framework/library + infra/DB/platform.
   Include: runtime version, OS, deployment method (Docker/bare metal/serverless).

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

Identify the domain FIRST — determines which reference file to load in Phase 4.

| Domain | Signals | Reference File |
|---|---|---|
| **Frontend** | UI not rendering, CSS broken, component state wrong, hydration error, bundle error, browser-only bug, routing broken, form not submitting, WebSocket UI issue | `references/frontend-patterns.md` |
| **Backend** | API response wrong, auth failing, DB issue, background job silent, queue not consumed, file upload broken, rate limit wrong, session bug, ORM query wrong | `references/backend-patterns.md` |
| **Integration/Pipeline** | Webhook not firing, message queue dropped, microservice not responding, data transform wrong, ETL dropping rows, CI/CD broken, API gateway wrong, event not propagating | `references/integration-patterns.md` |
| **General/Cross-cutting** | Async/concurrency, environment mismatch, encoding, type bugs, caching, memory | `references/bug-patterns.md` |

Multiple domains? Load ALL relevant files. Frontend bug calling backend API = load both.

### 2B — Symptom-to-Category Map

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

### 2B — Meta-Checks (Run These First, Always)

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

4. **Is there more than one bug?**
   - First bug masking second bug?
   - Fix for Bug A revealing Bug B (which was always there)?

---

## PHASE 3 — ADVERSARIAL DIAGNOSIS

Execute in this exact order. Do not skip any step.

### 3.1 — ASSUME EVERYONE WAS WRONG

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

### 3.2 — LAST KNOWN GOOD ANALYSIS

If the bug is a regression (worked before, broken now):

- What EXACTLY changed between last working state and now?
- If code change: diff the relevant files. What lines changed?
- If dependency update: which version introduced it? (`git bisect` / changelog)
- If data change: what data exists now that didn't before?
- If infra change: what is different about the environment?

The answer is always in the delta. Find the delta.

### 3.3 — BINARY SEARCH THE FAILURE

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

### 3.4 — TRACE THE EXECUTION PATH

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

### 3.5 — FIND THE LIES

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

### 3.6 — FORENSIC LOGGING

Write debug logging code adapted to the user's actual stack.
Place a log at **every unchecked assumption** from 3.5.
Make the bug prove itself. Never guess.

**Core logging principle:** Log type + value + identity, not just value.

```
# Type + value (adapt to language)
Python:       print(f"[DEBUG] {var=}, type={type(var).__name__}, repr={repr(var)}")
JavaScript:   console.log('[DEBUG]', {var, type: typeof var, value: JSON.stringify(var)})
Java:         System.out.printf("[DEBUG] %s type=%s%n", var, var.getClass().getName());
Go:           log.Printf("[DEBUG] %T %+v", var, var)
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
```

### 3.7 — VERDICT

Give **one** root cause. Not a list. Not "possibly". Stated as fact.

Structure:
```
ROOT CAUSE: [one sentence, specific]

WHY THIS HAPPENED: [one sentence explaining the mechanism]

BEFORE:
[the broken code]

AFTER:
[the fixed code]

WHY THIS FIX WORKS: [one sentence]
```

Do not rewrite the whole file. Fix only the broken lines.

---

## PHASE 4 — DEEP PATTERN REFERENCE (Domain Router)

Load the reference file(s) matching the domain identified in Phase 2A.
Always load ALL files relevant to the bug — never just one if multiple apply.

| File | When to Load | Contents |
|---|---|---|
| `references/frontend-patterns.md` | Any UI/browser/CSS/bundle/routing bug | Rendering, hydration, state, CSS, forms, WebSocket, PWA, browser compat |
| `references/backend-patterns.md` | Any API/auth/DB/queue/job/session bug | REST/GraphQL, auth, ORM, background jobs, file upload, rate limiting, sessions |
| `references/integration-patterns.md` | Any webhook/queue/pipeline/microservice bug | Webhooks, message queues, event-driven, ETL, CI/CD, API gateway, service mesh |
| `references/bug-patterns.md` | Async, environment, encoding, type, memory, concurrency | 10 categories, 45 universal patterns |

Each reference file has: symptom → why → how to prove → how to fix.
Load them. Read them. Match the pattern. Do not guess.

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

4. IF STILL FAILING
   □ Next suspect: [second most likely from 3.1]
   □ Add this specific log to narrow it further: [exact log statement]
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
Mismatch → You fixed the wrong line. Re-read 3.5.
```

### Step 3 — Check for a second bug
```
First bug is fixed. New symptom is different from original.
→ Two bugs were present. First fix revealed the second.
→ Run Phase 3 again from scratch on the NEW symptom.
```

### Step 4 — Escalate to minimal reproduction
```
Strip everything. Create the smallest possible failing case:
- Remove all unrelated code
- Use hardcoded inputs
- Run in isolation (no DB, no network, no framework if possible)

If it still fails in isolation → core logic bug. Reread 3.3-3.5.
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

---

## IRONCLAD RULES

1. **Fix only what is broken.** Never rewrite the whole file.
2. **Never revisit closed paths.** Already tried = dead path. Move on.
3. **One verdict.** Not a hedge list. Commit to the answer.
4. **Always BEFORE / AFTER.** Never just the new code alone.
5. **Forensic sentinel log.** Every fix gets a sentinel log to confirm it runs.
6. **Never assume.** Every assumption gets a log or assertion.
7. **Meta-check first.** Always verify the debugging setup before the code.
8. **Intermittent?** Only: async timing, shared state, race conditions, resource exhaustion.
9. **Silent failure?** Find the swallow. Something is catching and dropping the error.
10. **Works locally, fails in prod?** Always environment: config, secrets, version, load, timing.
11. **State not updating?** Find the interception layer between action and handler.
12. **Fix didn't work?** Run Phase 6. Do not repeat Phase 3 with the same assumptions.
13. **Two different symptoms?** Two bugs. Treat them separately.
14. **Recent change caused it?** The delta is the bug. Diff it. Revert it. Prove it.
