# ☢️ Nuclear Bug Fix — Claude Code Skill

> **The most powerful bug-fixing skill for Claude Code.**  
> Built for bugs that survive code review, careful planning, and multiple fix attempts.

---

## 👨‍💻 Created By

**Dr. Ajay Data**  
Founder & CEO, [Data Ingenious Technologies](https://www.dataingenious.com)  
Creator of [XgenPlus](https://www.xgenplus.com) — Enterprise Email & Communication Platform  
Jaipur, Rajasthan, India

> *"Most AI tools tell you what might be wrong. This skill tells you what IS wrong — and doesn't stop until the bug is dead."*  
> — Dr. Ajay Data

---

## 🧠 What This Is

`nuclear-bug-fix` is a Claude Code skill — a structured methodology that transforms Claude from a generic code reviewer into an **adversarial senior engineer** whose only job is to find and fix the bug.

It was born from real production debugging sessions where standard code review, careful planning, and multiple AI-assisted fix attempts all failed. The skill captures that hard-won methodology and makes it repeatable for any bug, on any stack.

---

## ⚡ What Makes It Different

| Standard Code Review | ☢️ Nuclear Bug Fix |
|---|---|
| Gives a list of suggestions | Commits to **one verdict** |
| Revisits already-tried fixes | Enforces **closed paths** — never repeats |
| No deployment verification | **Sentinel log** confirms fix is actually running |
| Generic "add some logging" | **Forensic logging** at every unverified assumption |
| Stops after first attempt | **6-phase escalation loop** — never gives up |
| Reviews only what's shown | **Meta-checks** the debugging setup itself |
| Framework-specific | Works on **any stack, any language** |

---

## 📦 Skill Contents

```
nuclear-bug-fix/
├── SKILL.md                          # Core methodology — 6 phases, 14 rules
└── references/
    ├── frontend-patterns.md          # 10 categories, 32 patterns
    ├── backend-patterns.md           # 9 categories, 28 patterns
    ├── integration-patterns.md       # 7 categories, 30 patterns
    └── bug-patterns.md               # 10 categories, 45 universal patterns
```

**Total: 36 categories · 135 patterns · 1,400+ lines of methodology**

Every pattern has 4 fields: **Symptom → Why → Prove it → Fix it**

---

## 🗂️ Coverage

### 🖥️ Frontend
Rendering & display bugs, CSS broken in prod, hydration mismatches (SSR),  
infinite render loops, state management, routing failures, form submission,  
async data racing, WebSocket, build/bundle issues, browser compatibility, CORS,  
localStorage failures, performance & memory leaks

### ⚙️ Backend
API response wrong, request body missing, route not matched, duplicate requests,  
JWT/auth failures, ORM wrong queries, N+1 queries, migration issues, background  
jobs silently failing, file upload corrupt, session contamination, rate limiting  
not working, errors swallowed in logs, external service integration failures

### 🔗 Integration & Pipelines
Webhooks not received/duplicate/out-of-order, message queue consumer lag,  
duplicate message processing, microservice contract drift, cascading failures,  
ETL rows silently dropped, schema change breaking pipeline, CI/CD passes but  
app broken, environment variables missing in deploy, distributed saga failures,  
API gateway header stripping, mTLS service mesh failures

### 🔬 Universal (Any Stack)
Async race conditions, stale closures, deadlocks, type coercion, integer overflow,  
timezone bugs, encoding mismatches, null/empty edge cases, environment mismatch,  
wrong code deployed, log level hiding errors, memory leaks, connection pool  
exhaustion, off-by-one errors, mutation during iteration

---

## 🚀 Installation

### Step 1 — Download the skill file
Download `nuclear-bug-fix.skill` from the [Releases](https://github.com/ajaydata-vision/nuclear-bug-fix-/releases) page  
or clone this repository.

### Step 2 — Install in Claude Code
```bash
claude skills add /path/to/nuclear-bug-fix.skill
```

### Step 3 — Verify installation
```bash
claude skills list
# nuclear-bug-fix should appear in the list
```

That's it. The skill activates **automatically** — no special command needed.

---

## 💬 How to Use

### Just describe your bug naturally. The skill activates automatically.

These phrases trigger it:

```
"I've tried everything and still can't fix this bug"
"Code review didn't find anything but it's still broken"
"The script runs but nothing gets set"
"Works locally but fails in production"
"I applied the fix but the bug is still there"
"Nothing works, help me find the bug"
"It's intermittent — only fails sometimes"
"The API returns 200 but nothing changes"
```

### What happens next

Claude will ask you **8 targeted intake questions** (one message, not a back-and-forth):

1. **Symptom** — what happens vs what should happen
2. **Failure point** — exactly where it breaks
3. **Recent changes** — what changed before the bug appeared
4. **Closed paths** — what you've already tried (these are locked out)
5. **Existing logs** — any logs or stack traces you already have
6. **The code** — just the broken section, not the whole file
7. **Stack** — language + framework + infra
8. **Consistent or intermittent** — always fails, or sometimes?

Then Claude executes the full methodology and gives you **one verdict with a BEFORE/AFTER fix**.

---

## 🔬 The 6-Phase Methodology

```
PHASE 1 — INTAKE          Collect 8 signals. Extract from conversation. Never re-ask.
PHASE 2 — TRIAGE          Classify domain (Frontend/Backend/Integration/General).
                           Run meta-checks: is the right code even running?
PHASE 3 — ADVERSARIAL     Reset all assumptions. Trace execution. Find the lies.
           DIAGNOSIS       Binary search the failure. Forensic logs at every assumption.
                           ONE verdict. BEFORE/AFTER fix. Sentinel log in every fix.
PHASE 4 — PATTERN         Load domain-specific reference file(s). Match the pattern.
           REFERENCE
PHASE 5 — VERIFY          4-step checklist. Confirm fix ran. Confirm no regression.
PHASE 6 — ESCALATION      If fix didn't work: 5-step escalation loop.
           LOOP            Never repeats the same approach twice.
```

---

## 🔑 The 14 Ironclad Rules

1. Fix only what is broken — never rewrite the whole file
2. Never revisit closed paths — already tried = dead path
3. One verdict only — not a hedge list, commit to the answer
4. Always BEFORE / AFTER — never just the new code
5. Sentinel log in every fix — confirm the fix is actually running
6. Never assume — every assumption gets a log or assertion
7. Meta-check first — verify the debugging setup before the code
8. Intermittent? Focus only on async timing, shared state, race conditions
9. Silent failure? Find the swallow — something is catching the error
10. Works locally, fails in prod? Always environment: config, secrets, version
11. State not updating? Find the interception layer
12. Fix didn't work? Run Phase 6 — do not repeat Phase 3
13. Two different symptoms? Two bugs — treat them separately
14. Recent change caused it? The delta is the bug — diff it, revert it, prove it

---

## 🧪 Smoke Test Results

| Test | Result |
|---|---|
| SKILL.md structure (6 phases) | ✅ Pass |
| All phases have content | ✅ Pass |
| Domain router present | ✅ Pass |
| All critical keywords present | ✅ Pass |
| All 135 patterns have 4 fields | ✅ Pass |
| GitHub push | ✅ Pass |
| Package validation | ✅ Pass |

---

## 🤝 Contributing

Found a bug pattern not covered? Open a PR adding it to the relevant reference file.

Pattern format:
```markdown
### Pattern: [Short descriptive name]
**Symptom:** What it looks like from the outside
**Why:** The actual mechanism causing it
**Prove:** Exact steps to confirm this is the cause
**Fix:** Exact fix with BEFORE/AFTER where applicable
```

---

## 📄 License

MIT License — free to use, share, and build upon.  
If this skill saves your team hours of debugging, a ⭐ on the repo would be appreciated.

---

## 🙏 Acknowledgements

Built with [Claude Code](https://claude.ai/code) by Anthropic.  
Methodology developed through real production debugging sessions at  
[Data Ingenious Technologies](https://www.dataingenious.com).

---

<p align="center">
  <strong>Created by Dr. Ajay Data · Data Ingenious Technologies · Jaipur, India</strong><br/>
  <a href="https://www.dataingenious.com">dataingenious.com</a> ·
  <a href="https://www.xgenplus.com">xgenplus.com</a> ·
  <a href="https://github.com/ajaydata-vision">github.com/ajaydata-vision</a>
</p>
