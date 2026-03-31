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

```text
nuclear-bug-fix/
├── VERSION                               # Current release version (1.4)
├── CHANGELOG.md                          # 1.4 release notes and release history
├── SKILL.md                              # Core methodology - 6 phases, DDx gate, 35 rules
├── setup                                 # Root setup entrypoint for git-cloned installs
├── setup.ps1                             # Root PowerShell setup entrypoint
├── references/                           # 9 reference files for patterns, DDx, and external intelligence
├── benchmarks/                           # 127 benchmark cases plus suite metadata
├── scripts/
│   ├── install.py                        # Local repo installer into Claude's skills directory
│   ├── install.sh                        # One-line installer for macOS/Linux
│   ├── install.ps1                       # One-line installer for Windows PowerShell
│   ├── update.sh                         # Bash updater for installed skill directories
│   ├── update.ps1                        # PowerShell updater for installed skill directories
│   └── build_skill.py                    # Deterministic packaging, release manifest, and validation
└── dist/
    ├── nuclear-bug-fix.skill             # Packaged release artifact for shipped updates and validation
    └── release.json                      # Single source of truth for released version metadata
```

**Current repo snapshot:** 9 reference files, 127 benchmark cases, and 3,800+ lines across `SKILL.md` and `references/`.
**Current release:** `1.4`  
**Release date:** `2026-03-31`

The reference files follow the same pattern language: **Symptom -> Why -> Prove -> Fix**

---

## 🌐 External Intelligence Layer

When internal analysis isn't enough, the skill searches external sources **before writing forensic logs** — because a known bug has a known fix, and finding it takes 2 minutes vs rediscovering it in hours.

### What it searches (in priority order)

| Tier | Source | What It Finds |
|---|---|---|
| 1 | **Official Docs** | API misuse, version-specific behavior, deprecations |
| 1 | **Official Changelog** | Breaking changes between versions, regressions |
| 2 | **GitHub Issues** | Confirmed bugs, workarounds, fixed-in versions |
| 2 | **Stack Overflow** | Community fixes with exact error text matching |
| 3 | **RFC Specifications** | Protocol violations (HTTP, OAuth, JWT, WebSocket, SMTP) |
| 4 | **CVE Database** | Known security vulnerabilities in the version |
| 4 | **Package Advisories** | npm audit, pip-audit, govulncheck |
| 5 | **MDN / caniuse** | Browser API support, compatibility quirks |

### RFC Coverage

The skill knows exactly which RFC to check for which protocol:

```
HTTP semantics     → RFC 9110    OAuth 2.0      → RFC 6749
HTTP/1.1 syntax    → RFC 9112    PKCE           → RFC 7636
HTTP/2             → RFC 9113    JWT            → RFC 7519
HTTP Cookies       → RFC 6265    JSON Web Keys  → RFC 7517
WebSocket          → RFC 6455    SMTP           → RFC 5321
HTTP Auth          → RFC 7235    IMAP4rev2      → RFC 9051
Timestamps/Dates   → RFC 3339    JSON           → RFC 8259
Base64             → RFC 4648    URI Syntax     → RFC 3986
```

### Version Intelligence

Exact version numbers are now **required** at intake. The skill uses them to:
- Flag versions < 6 months old (possible unpatched bugs)
- Flag versions > 2 years old (missing critical patches)
- Detect peer dependency mismatches
- Search changelogs between working version and current
- Look up CVEs for the exact version in use

### Search Trigger Conditions

The skill automatically triggers external search when:
```
✓ Error message contains a library/framework name
✓ Bug started after a version update
✓ Behavior contradicts what the official docs say
✓ Bug involves a protocol (HTTP, WebSocket, OAuth, SMTP, gRPC)
✓ Bug is auth/security related
✓ Framework version is < 6 months old
✓ Code cannot be explained as broken just by reading it
```

---

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

Claude Code discovers skills from directories, not from a special import command:

- Personal skills: `~/.claude/skills/`
- Project skills: `.claude/skills/`

### Git install

This repo intentionally ships two root setup files:

- `./setup` for `bash`/`sh` on macOS, Linux, Git Bash, or WSL
- `.\setup.ps1` for Windows PowerShell

Use the setup file that matches the shell you are currently running inside Claude Code.

Personal install:
```bash
git clone --single-branch --depth 1 https://github.com/ajaydata-vision/nuclear-bug-fix- ~/.claude/skills/nuclear-bug-fix
cd ~/.claude/skills/nuclear-bug-fix
./setup
```

Project install:
```bash
git clone --single-branch --depth 1 https://github.com/ajaydata-vision/nuclear-bug-fix- .claude/skills/nuclear-bug-fix
cd .claude/skills/nuclear-bug-fix
./setup
```

Windows PowerShell from a git clone:
```powershell
git clone --single-branch --depth 1 https://github.com/ajaydata-vision/nuclear-bug-fix- $HOME\.claude\skills\nuclear-bug-fix
Set-Location $HOME\.claude\skills\nuclear-bug-fix
.\setup.ps1
```

### Script install

macOS / Linux personal install:
```bash
curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.sh | bash
```

macOS / Linux project install:
```bash
curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.sh | bash -s -- --project
```

Windows PowerShell personal install:
```powershell
irm https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.ps1 | iex
```

Windows PowerShell project install:
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.ps1))) -Project
```

### Install from an existing clone

Personal install:
```bash
python3 scripts/install.py
```

Project install:
```bash
python3 scripts/install.py --scope project
```

### Verify installation

Check that the skill directory exists:
```bash
ls ~/.claude/skills/nuclear-bug-fix
# or
ls .claude/skills/nuclear-bug-fix
```

Then restart Claude Code and ask:
```text
What skills are available?
```

The `setup` and `setup.ps1` entrypoints make the git-clone flow work like other Claude Code skill packs: clone into the skill directory, run setup once, and restart Claude Code. The `dist/nuclear-bug-fix.skill` file is still shipped as a packaged release artifact for updates and release validation.

### Update an installed skill

Bash / Git Bash / WSL:
```bash
bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh
# or, from a project root
bash .claude/skills/nuclear-bug-fix/scripts/update.sh
```

Windows PowerShell:
```powershell
& "$HOME\.claude\skills\nuclear-bug-fix\scripts\update.ps1"
# or, from a project root
& ".\.claude\skills\nuclear-bug-fix\scripts\update.ps1"
```

Maintainer note: when the update flow changes, keep `scripts/update.sh` and `scripts/update.ps1` behavior in sync.

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

## 🔑 Rule Highlights

The full skill currently defines 35 rules in SKILL.md; the list below is the condensed README version.

1. Fix only what is broken — never rewrite the whole file
2. Never revisit closed paths — already tried = dead path
3. One verdict only — not a hedge list, commit to the answer
4. Always BEFORE / AFTER — never just the new code
5. Sentinel log in every fix — confirm the fix is actually running
6. Never assume — every assumption gets a log or assertion
7. Meta-check first — verify the debugging setup before the code
8. Search before concluding — Phase 3.6 runs before forensic logs. Known bug = known fix
9. Exact versions required — never accept "latest", they unlock known-bug detection
10. Docs trump assumptions — if official docs say it works differently, the code is wrong
11. RFC is ground truth for protocols — HTTP, OAuth, JWT, WebSocket, SMTP checked against spec
12. Intermittent? Focus only on async timing, shared state, race conditions
13. Silent failure? Find the swallow — something is catching the error
14. Works locally, fails in prod? Always environment: config, secrets, version
15. State not updating? Find the interception layer
16. Fix didn't work? Run Phase 6 — do not repeat Phase 3
17. Two different symptoms? Two bugs — treat them separately
18. Recent change caused it? The delta is the bug — diff it, revert it, prove it

---

## 🧪 Smoke Test Results

| Test | Result |
|---|---|
| SKILL.md structure (6 phases) | ✅ Pass |
| Domain router + DDx gate present | ✅ Pass |
| Reference files present (9) | ✅ Pass |
| Benchmark cases present (127) | ✅ Pass |
| Every case has prompt/evaluator/verify | ✅ Pass |
| Semantic release version (`1.4`) | ✅ Pass |
| Deterministic artifact validation | ✅ Pass |
| Release manifest ↔ packaged version alignment | ✅ Pass |

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

