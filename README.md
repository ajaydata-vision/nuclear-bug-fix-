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
| Generic "add some logging" | **Targeted smoking-gun Prove** per pattern |
| Stops after first attempt | **6-phase escalation loop** — never gives up |
| Reviews only what's shown | **Meta-checks** the debugging setup itself |
| Framework-specific | Works on **any stack, any language** |
| Issues verdict based on consistency | **DDx Gate** — eliminates alternatives before verdict |

---

## 📊 Benchmark Results

Scored against 161 real-world bug cases across 13 domains:

| Metric | Score |
|---|---|
| **Mean score** | **94.2 / 100** |
| Cases scoring 85+ | 25 / 25 (100%) |
| Single-shot HIGH confidence rate | 96% |

**By domain:**

| Domain | Patterns | Mean |
|---|---:|---:|
| Java Enterprise (Servlet/JSP/Spring/Kafka/Loom) | 49 | 96.9 |
| React Native (Metro/Navigation/Reanimated/Expo) | 26 | 96.2 |
| Frontend JS/TS (React/Vue/vanilla/async/CSS) | 51 | 94.7 |
| Kafka / Messaging | — | 92.3 |
| PHP (Laravel + plain PHP) | 45 | 94.6 |
| Backend, Integration, Mobile | 38–45 | 91–95 |

---

## 📦 What's Inside

```
nuclear-bug-fix/
├── SKILL.md                      # Core methodology — 6 phases, DDx gate, 35 ironclad rules
├── references/                   # 14 reference files — 288 patterns (100% Prove coverage)
│   ├── java-patterns.md          # 49 patterns: Servlet/JSP/NIO/Threading/JVM/Spring/Kafka/Loom
│   ├── frontend-patterns.md      # 53 patterns: React/Vue/Angular/vanilla JS/CSS/async/TypeScript
│   ├── react-native-patterns.md  # 26 patterns: Metro/Navigation/FlatList/Reanimated/Expo/perms
│   ├── php-patterns.md           # 45 patterns: Execution model/OPcache/type-system/Laravel/PHP-FPM/PDO
│   ├── backend-patterns.md       # 38 patterns: API/auth/DB/jobs/session/rate-limit/security
│   ├── integration-patterns.md   # 32 patterns: webhooks/queues/microservices/ETL/K8s/CI-CD
│   ├── bug-patterns.md           # 45 patterns: async/types/env/caching/memory — any stack
│   ├── intermittent-race-bugs.md # Race conditions, Heisenbugs, TSan tools
│   ├── ddx-gate.md               # ACH methodology, evidence matrix, cognitive bias catalog
│   ├── external-intelligence.md  # RFC lookup, changelog analysis, CVE database
│   ├── python-desktop-patterns.md
│   ├── bridge-adapter-patterns.md
│   ├── windows-packaging-patterns.md
│   └── world-methods.md
├── benchmarks/                   # 161 benchmark cases across 13 domains
└── dist/
    ├── nuclear-bug-fix.skill     # Packaged release artifact
    └── release.json              # Release manifest
```

**Current release:** `1.16` · **Release date:** `2026-04-05`  
**Total patterns:** 288 · **All with targeted Prove sections** · **100% Prove coverage**

---

## 🎯 The Single-Shot Approach

Most AI debugging stops at "here's what might be wrong." Nuclear Bug Fix is engineered for **one correct answer on the first attempt**.

**1. Pattern Pre-Load at Triage**  
Before diagnosis begins, the skill loads the domain reference file and identifies your top 1–2 candidate patterns. Every step of Phase 3 is then informed by the specific pattern — not generic logic.

**2. Targeted Smoking-Gun Prove**  
Every pattern has a precise Prove section — the exact log, command, or check that produces output impossible to explain any other way. One log. Binary result. Gate closed.

**3. DDx Gate Before Verdict**  
Borrowed from medical differential diagnosis and the CIA's Analysis of Competing Hypotheses. Before issuing any verdict, the skill forces elimination of every plausible alternative. Consistency ≠ proof.

**4. Confidence Score on Every Verdict**  
`HIGH (90–95%)` — Direct proof, all alternatives eliminated.  
`MEDIUM (70–85%)` — Consistent evidence, alternatives eliminated mainly by absence.  
`LOW / BLOCK` — Evidence is ambiguous — collects more before proceeding.

---

## 🌐 Domain Coverage

**☕ Java Enterprise** — Servlet lifecycle, JSP/JSTL, NIO, threading, JVM/ClassLoader, JDBC/HikariCP, Spring Boot (Transactional, Async, Scheduling, Cache, Security, Hibernate, WebFlux), Kafka consumer patterns, Java 21 virtual threads

**📱 React Native** — Metro bundler, React Navigation, FlatList, Reanimated worklets, Expo/EAS, AsyncStorage, iOS permissions, native modules, New Architecture (JSI/TurboModules)

**🖥️ Frontend (Web)** — SSR hydration, CSS, state management, async data racing, WebSocket, build/bundle, CORS, localStorage, vanilla JS DOM, Promise traps, TypeScript runtime bugs, dynamic chunk 404 after deploy

**⚙️ Backend** — API failures, auth (JWT/session/cookie/SameSite), ORM, N+1, background jobs, session leaks, rate limiting, external service failures, connection pool exhaustion

**🔗 Integration & Pipelines** — Webhooks, Kafka, microservice cascading failures, ETL, CI/CD, K8s readiness probes, API gateway header stripping, distributed sagas

**🐍 Python Desktop / Bridge / Packaged** — PyQt6/qasync, Baileys-style bridges, PyInstaller frozen runtime

**🐘 PHP** — OPcache stale bytecode, loose comparison traps (`==` vs `===`, `empty()`, `in_array()`), Laravel (Eloquent N+1, queue silent fail, service container, config cache, middleware, events), PHP-FPM exhaustion, PDO ERRMODE_SILENT, transaction not committed, charset mismatch, CLI/FPM version split, `.env` not loaded in cron

**🔬 Universal** — Race conditions, Heisenbugs, Mandelbugs, deadlocks, type coercion, timezone bugs, environment mismatch, memory leaks

---

## 🚀 Installation

**macOS / Linux (personal):**
```bash
curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.sh | bash
```

**macOS / Linux (project):**
```bash
curl -fsSL https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.sh | bash -s -- --project
```

**Windows PowerShell (personal):**
```powershell
irm https://raw.githubusercontent.com/ajaydata-vision/nuclear-bug-fix-/main/scripts/install.ps1 | iex
```

**Git clone:**
```bash
git clone --single-branch --depth 1 https://github.com/ajaydata-vision/nuclear-bug-fix- ~/.claude/skills/nuclear-bug-fix
cd ~/.claude/skills/nuclear-bug-fix && ./setup
```

### Update

```bash
bash ~/.claude/skills/nuclear-bug-fix/scripts/update.sh
```
Or type `/nuclear-bug-fix update` in Claude Code.

---

## 💬 How to Use

Just describe your bug naturally. The skill activates automatically on phrases like:

```
"I've tried everything and still can't fix this bug"
"Works locally but fails in production"
"I applied the fix but the bug is still there"
"The API returns 200 but nothing changes"
"It's intermittent — only fails sometimes"
"Nothing works, help me find the bug"
```

Claude collects 8 targeted signals, loads the matching domain reference, identifies the top candidate pattern, runs a targeted Prove, passes the DDx Gate, and gives you **one verdict with BEFORE/AFTER fix code**.

---

## 🔬 The 6-Phase Methodology

```
PHASE 0 — REPRODUCE     Stimulate, don't simulate. Preserve evidence first.
PHASE 1 — INTAKE        8 signals. Extract from conversation. Never re-ask.
PHASE 2 — TRIAGE        Load domain file. Identify CP-1/CP-2 candidate patterns.
                         Meta-checks: is the right code even running?
PHASE 3 — ADVERSARIAL   Targeted Prove from CP-1. Binary search. DDx Gate.
           DIAGNOSIS     Eliminate every alternative before verdict.
PHASE 4 — PATTERN       Full reference review. Confirm or revise diagnosis.
PHASE 5 — VERIFY        Sentinel log confirms fix is running. 4-step checklist.
PHASE 6 — ESCALATION    If fix failed: 5-step loop. Never same approach twice.
```

---

## 🧪 v1.13 Status

| Check | Status |
|---|---|
| 6 phases, DDx Gate, 35 rules | ✅ |
| 13 reference files, 241 patterns, 100% Prove coverage | ✅ |
| 161 benchmark cases, all 3 files per case | ✅ |
| Benchmark score: 94.2 / 100 mean | ✅ |
| Release manifest ↔ archive version aligned | ✅ |
| `/nuclear-bug-fix update` delivers v1.13 | ✅ |

---

## 🤝 Contributing

Found a pattern not covered? Open a PR. Pattern format:

```markdown
### Pattern: [Short descriptive name]
**Symptom:** What it looks like
**Why:** The actual mechanism
**Prove:** Exact log/command producing pathognomonic output
**Fix:** Exact fix with BEFORE/AFTER code
```

---

## 📄 License

MIT — free to use, share, and build upon.  
If this saves your team hours of debugging, a ⭐ is appreciated.

---

<p align="center">
  <strong>Created by Dr. Ajay Data · Data Ingenious Technologies · Jaipur, India</strong><br/>
  <a href="https://www.dataingenious.com">dataingenious.com</a> ·
  <a href="https://www.xgenplus.com">xgenplus.com</a> ·
  <a href="https://twitter.com/dataingenious">@dataingenious</a> ·
  <a href="https://github.com/ajaydata-vision">github.com/ajaydata-vision</a>
</p>
