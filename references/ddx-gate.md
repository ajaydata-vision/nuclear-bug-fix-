# Differential Diagnosis Gate — Reference

The methodology behind step 3.9. Built on:
- CIA's Analysis of Competing Hypotheses (Richards Heuer, 1999)
- Medical Differential Diagnosis (DDx) practice
- Scientific falsifiability (Karl Popper)
- Pre-mortem analysis (Gary Klein)

---

## WHY THIS GATE EXISTS

The most common cause of a wrong diagnosis is not stupidity. It is confirmation bias.

The conventional debugging process:
1. Identify a plausible hypothesis
2. Search for evidence that supports it
3. Find supporting evidence → issue verdict

The problem: much evidence that supports your hypothesis also supports alternatives.
You never checked whether the evidence is EXCLUSIVE to your hypothesis.
You diagnosed a shadow, not the cause.

ACH shifts the analytical focus from proving a favoured hypothesis
to disproving less likely alternatives — conclusions reached through
elimination, not assumption.

This gate forces that shift.

---

## THE CORE DISTINCTION: CONSISTENT vs DIAGNOSTIC EVIDENCE

```
CONSISTENT evidence:   Does not contradict the hypothesis.
                       Could be explained by multiple hypotheses.
                       Proves nothing.

DIAGNOSTIC evidence:   Is INCONSISTENT with one or more alternatives.
                       Can ONLY be explained by the surviving hypothesis.
                       Actually eliminates alternatives.
```

**Example:**

Bug: API returns 200 but database record not updated.

Evidence: "The log shows the API handler was reached."

- Consistent with: Code bug in handler (your hypothesis)
- Consistent with: Transaction rolled back silently (alternative 1)
- Consistent with: Wrote to wrong database connection (alternative 2)

This evidence is CONSISTENT with all three. It eliminates none.

**Diagnostic evidence would be:**

"The log shows `COMMIT` executing with 0 rows affected."
- Consistent with: Transaction rolled back (now this is the hypothesis)
- INCONSISTENT with: Code bug (the code ran and committed successfully)
- INCONSISTENT with: Wrong connection (committed, just nothing to commit)

That eliminates two alternatives. The rolled-back transaction is now the diagnosis.

---

## COGNITIVE BIAS CATALOG

Know these. They are the enemies of correct diagnosis.

### Confirmation Bias
Searching for evidence that confirms the hypothesis you already believe.
Ignoring evidence that contradicts it.
**Antidote:** Explicitly search for evidence that would DISPROVE your hypothesis.

### Anchoring Bias
Over-weighting the first explanation that seemed plausible.
All subsequent evidence interpreted through that anchor.
**Antidote:** Generate all competing hypotheses BEFORE collecting evidence.
Do not let one hypothesis dominate the list-building step.

### Availability Bias
Diagnosing the bug as the most recent or most memorable bug you fixed.
"This looks like the cache invalidation bug from last month."
**Antidote:** Force yourself to list domain-appropriate alternatives.
The bug that comes to mind first is often not the bug.

### Premature Closure
Stopping evidence collection once you have a plausible explanation.
Not checking if other explanations are equally supported.
**Antidote:** The gate blocks the verdict until alternatives are eliminated.
You cannot close early if the gate is not passed.

### Satisficing
Going with the first answer that seems supported by evidence.
Efficient, but makes no investment in protection against being wrong.
**Antidote:** The gate is not satisficing. It requires elimination, not plausibility.

### Groupthink
Agreeing with the consensus without independent verification.
"The team already thinks it's the race condition."
**Antidote:** Run the gate independently. The evidence matrix does not care what the team thinks.

---

## COMMON FALSE DIAGNOSES BY DOMAIN

These are bugs that "look like X" but are actually Y.
Reference this list when generating competing hypotheses.

### Backend / API

| Looks Like | But Often Is |
|---|---|
| Bug in handler code | Transaction silently rolled back |
| Bug in handler code | Writing to wrong DB connection/schema |
| Auth token rejected | Token valid but sent in wrong header format |
| Auth token rejected | Server clock skew invalidating JWT exp |
| Slow API | N+1 ORM queries, not slow handler logic |
| 500 error in handler | Middleware upstream throwing before handler reached |
| Missing rows in response | Pagination applied — not missing, just on page 2 |
| DB write succeeded | Wrote to replica — primary has it, replica doesn't yet |

### Frontend / UI

| Looks Like | But Often Is |
|---|---|
| Click handler not firing | Invisible overlay absorbing the click |
| State not updating | Mutating a copy instead of the original object |
| Component not re-rendering | Memoization too aggressive |
| API call failing | CORS preflight blocked — the actual request never fires |
| Data missing on load | Race: second call resolves first and overwrites first call's data |
| CSS broken in prod | Tailwind purge removed class used dynamically |
| Form not submitting | `e.preventDefault()` not called — or called in wrong place |

### Async / Concurrency

| Looks Like | But Often Is |
|---|---|
| Random value corruption | Two threads sharing the same mutable object |
| Intermittent failure | Test ordering — test B contaminates state for test A |
| Value null after await | Operation not awaited — result consumed immediately |
| Race condition | Not a race — single thread, event loop, wrong order of operations |
| Deadlock | Not a deadlock — infinite loop consuming CPU, no threads blocked |

### Environment / Config

| Looks Like | But Often Is |
|---|---|
| Bug in code | Wrong code is deployed — old version running |
| Code works, env broken | Config value correct in .env but not loaded at runtime |
| Works locally, fails in CI | Case-sensitive file path (Linux CI, macOS local) |
| Works locally, fails in prod | Dependency version pinned differently between environments |
| SSL error | Certificate hostname mismatch, not expiry |

### Integration / Pipeline

| Looks Like | But Often Is |
|---|---|
| Webhook not arriving | Signature validation failing silently — webhook received and rejected |
| Message queue bug | Consumer subscribed to wrong queue name (typo) |
| ETL dropping rows | Rows present but failing silent validation — dropped to /dev/null |
| Microservice not responding | Service responding, but load balancer routing to crashed instance |

---

## FULL ACH EVIDENCE MATRIX TEMPLATE

Copy this for each diagnosis session.

```
BUG SYMPTOM: [describe]

HYPOTHESES:
  PH:   [primary — your current diagnosis]
  CH-1: [strongest alternative]
  CH-2: [second alternative]
  CH-3: [third alternative]

EVIDENCE COLLECTED:
  E-1: [description of evidence item 1]
  E-2: [description of evidence item 2]
  E-3: [description of evidence item 3]
  E-4: [description of evidence item 4]
  E-5: [description of evidence item 5]

MATRIX:
(C = Consistent, I = Inconsistent, N = Neutral/Not applicable)

| Evidence | PH | CH-1 | CH-2 | CH-3 |
|---|---|---|---|---|
| E-1 | C | C | C | C |
| E-2 | C | C | I | C |
| E-3 | C | I | C | C |
| E-4 | C | C | C | I |
| E-5 | C | C | C | C |

SCORING (count I's per column):
  PH:   0 inconsistencies → survives
  CH-1: 1 inconsistency   → check if E-3 is truly incompatible
  CH-2: 1 inconsistency   → check if E-2 is truly incompatible
  CH-3: 1 inconsistency   → check if E-4 is truly incompatible

ELIMINATION THRESHOLD:
  1 strong inconsistency → eliminated (if evidence is reliable)
  0 inconsistencies → NOT eliminated → collect more evidence
  
RELIABLE INCONSISTENCY = evidence that makes the hypothesis logically impossible,
not merely less likely. "Seems unlikely" is not elimination.
```

---

## SENSITIVITY ANALYSIS

After generating the verdict, test its robustness:

```
SENSITIVITY TEST 1 — Key Evidence:
  "If [most important piece of supporting evidence] turned out to be wrong:"
  → Would the verdict still hold?
  YES → High confidence. Evidence independent.
  NO  → Medium confidence. Flag the dependency explicitly.

SENSITIVITY TEST 2 — Alternative Evidence:
  "If [next most plausible CH] turned out to be correct:"
  → What evidence would look different?
  → Is there a test we could run to check this specific case?
  If yes → run the test before issuing the verdict.

SENSITIVITY TEST 3 — Assumption Test:
  "List every assumption embedded in the diagnosis."
  (E.g., "We assume the logs are from the correct execution.")
  → Which assumptions have we verified?
  → Which are still unverified?
  Unverified assumptions = unresolved risk in the diagnosis.
```

---

## CONFIDENCE CALIBRATION GUIDE

```
HIGH (90-95%):
  □ Primary hypothesis directly confirmed by forensic logs
    (not just "consistent with" — directly observed in output)
  □ All 3 competing hypotheses eliminated by diagnostic (inconsistent) evidence
  □ Key evidence passes sensitivity test
  □ No unverified assumptions remain
  Example: "The log shows the exact null pointer dereference at line 47.
            The race condition (CH-1) is eliminated because the code is
            single-threaded. The caching hypothesis (CH-2) is eliminated
            because we bypassed cache and it still failed. The env config
            hypothesis (CH-3) is eliminated because we confirmed the
            correct value is set."

MEDIUM (70-85%):
  □ Primary hypothesis consistent with all evidence
  □ Competing hypotheses eliminated mainly by ABSENCE of evidence
    (nothing supports them, but no smoking-gun inconsistency either)
  OR:
  □ One competing hypothesis eliminated by inconsistent evidence
  □ Others eliminated only by absence
  OR:
  □ Key evidence fails sensitivity test (verdict depends on single piece)
  Action: State the dependency. Specify what would change the diagnosis.

LOW (50-65%):
  □ Primary hypothesis is plausible
  □ At least one competing hypothesis is also plausible with current evidence
  □ No diagnostic evidence to distinguish between them
  Action: DO NOT ISSUE VERDICT. Run Step 5 — evidence collection plan.
  State explicitly: "Cannot distinguish between [PH] and [CH-x] with
  current evidence. Need [specific evidence] to separate them."

BLOCK (<50%):
  □ Evidence is genuinely ambiguous between two or more explanations
  □ Evidence matrix shows no inconsistencies for multiple hypotheses
  Action: GATE BLOCKED. Collect more evidence.
  This is not a failure — it is intellectual honesty.
  A wrong verdict costs more than admitting uncertainty.
```

---

## PRE-MORTEM CHECK

Before issuing any verdict, run this 60-second check:

```
"Imagine we apply this fix and it does not resolve the bug.
What would have been wrong with our diagnosis?"

Write down the answer.

If the answer is: "[CH-1] was actually the cause" →
  Ask: Did we actually eliminate CH-1 with real evidence?
  Or did we just decide it was less likely?

If the answer is: "We missed [thing we didn't check]" →
  Check that thing before issuing the verdict.

If the answer is: "Nothing — we have direct proof" →
  Proceed. The pre-mortem found no vulnerability.
```

This takes 60 seconds. It prevents hours of applying the wrong fix.

---

## ESCALATION: WHEN THE GATE CANNOT BE PASSED

Sometimes you genuinely cannot collect the eliminating evidence:
- No access to production logs
- Cannot reproduce the bug
- External system with no observability
- Privacy/NDA constraints on data

In these cases, the verdict becomes probabilistic. Format:

```
CONFIDENCE: MEDIUM — Evidence is incomplete

MOST LIKELY CAUSE: [PH — with reasoning]

ALTERNATIVE STILL POSSIBLE: [CH-x — cannot be eliminated without [specific evidence]]

RECOMMENDATION:
  Apply fix for PH first (least invasive, highest probability).
  Monitor specifically for [what CH-x would produce] after the fix.
  If [CH-x indicator] appears → the fix was wrong → investigate CH-x next.

WHAT WOULD CHANGE THIS DIAGNOSIS:
  [exact evidence that would switch the verdict to CH-x]
```

This is not a failure. It is a calibrated, honest verdict with an explicit fallback plan.
It is far better than a high-confidence wrong answer.
