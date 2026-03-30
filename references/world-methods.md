# World's Best Debugging Methods

Research-backed methodologies that engineers worldwide swear by.
Synthesized from: David Agans' 9 Rules, Google SRE, NASA JPL practices,
Heisenbug taxonomy, 5 Whys (Toyota), Fishbone/Ishikawa, Fault Tree Analysis.

---

## METHOD 1 — AGANS' 9 RULES (The Debugging Bible)

David Agans' rules are considered the most universally applicable debugging methodology.
Used by hardware and software engineers across NASA, military, and commercial systems.
When engineers who debugged fast were studied, they all followed these rules intuitively.

### Rule 1: Understand the System
Before debugging, you must understand what the system is SUPPOSED to do.
If you don't understand a part of the system — that's where the bug is.
```
Read the docs. Read the source. Read the RFC. Know the intended design.
"If you don't understand it when you design it, you're more likely to mess up."
The part you skip reading is always where the bug hides.
```

### Rule 2: Make It Fail (On Demand)
You can only debug a failure you can reproduce consistently.
```
Do it again: Can you make it fail RIGHT NOW?
Start at the beginning: Don't start mid-sequence.
Stimulate, don't simulate: Use REAL conditions, not approximations.
  Real data → real failure.  Mock data → mock failure (useless).
Find the uncontrolled condition: What variable you're not controlling is causing the intermittence?
Record EVERYTHING: Screenshots, logs, sequence of actions. Every time.
Never throw away a debugging tool: The thing that helped you repro is gold.
```

### Rule 3: Quit Thinking and Look
The most violated rule. Engineers theorize when they should observe.
```
"Too many try to fix things based on a guess instead of gathering data."
See the failure directly. Watch it happen. Don't assume you know what happens.
See the details: The exact error, the exact value, the exact line.
Build instrumentation in: Add logging before you need it.
Watch out for Heisenberg: Does your observation change the bug?
  YES → Heisenbug. Change your approach (non-invasive observation only).
Guess only to FOCUS the search. Never guess to FIX without seeing.
```

### Rule 4: Divide and Conquer
Binary search the problem space. Narrow systematically.
```
Split the code path in half. Does the bug still occur?
YES → Bug is in the second half. Repeat.
NO  → Bug is in the first half. Repeat.
5–7 iterations isolates any bug to a single line.

For hardware and complex systems: isolate subsystems one at a time.
Simplify inputs until the minimum failing case is found.
The minimum failing case IS the bug's DNA.
```

### Rule 5: Change One Thing at a Time
The most commonly violated rule during "fix" attempts.
```
If you change two things and the bug goes away:
→ You don't know which thing fixed it.
→ You may have introduced a new bug with the other change.
→ You cannot write a test that proves it's fixed.

Change ONE variable. Test. Document. Revert if needed. Next variable.
This is slower in the moment. It is faster overall. Always.
```

### Rule 6: Keep an Audit Trail
Record every step. What you tried. What happened. What you concluded.
```
Without an audit trail:
- You'll repeat dead paths after 3 hours
- You can't hand off to another engineer
- You can't write a postmortem
- You can't prevent recurrence

Format: What I tried → What happened → What this means
The pattern in your failed attempts often points directly to the root cause.
```

### Rule 7: Check the Plug (Obvious First)
Before sophisticated analysis, check the embarrassingly simple things.
```
Is it plugged in? Is the server running? Is the port open?
Is the config file in the right location? Is the env var set?
Is it the right environment? Is the code actually deployed?
Is the process running? Is there disk space? Is there memory?

These take 30 seconds. Engineers skip them and waste 4 hours.
"Start at the beginning" — literally check if the system is on.
```

### Rule 8: Get a Fresh View
If you've been debugging for more than 2 hours without progress:
```
RUBBER DUCK DEBUGGING: Explain the bug out loud, step by step.
  As you articulate it precisely, you'll often find the flaw.
  The duck doesn't need to understand. You need to explain.

PAIR DEBUGGING: Another engineer's eyes see what you're blind to.
  You've been in the code too long. Familiarity = blindness.
  Junior engineers often find what seniors miss (no assumptions).

STEP AWAY: Sleep on it. The unconscious brain debugs.
  The "shower moment" is real. Forced rest often finds the answer.

CHALLENGE YOUR ASSUMPTIONS: If you're convinced it's X, deliberately look at Y.
  The real issue often lies in the least expected place.
```

### Rule 9: If You Didn't Fix It, It Ain't Fixed
The most important rule for verification.
```
"If the bug didn't disappear under the exact same conditions 
that caused it, you didn't fix it."

You must reproduce the original failure condition and confirm it no longer fails.
Not: "I think I fixed it."
Not: "It seems to work now."
Not: "It works in dev."

It must fail under the old conditions. Then not fail after the fix.
Under the SAME conditions. Same environment. Same input. Same load.
```

---

## METHOD 2 — BUG TAXONOMY (Know What You're Hunting)

Different bug types require fundamentally different strategies.

### Bohrbug — The Good Bug
```
Definition: Deterministic. Reproducible. Same input → same failure every time.
Named after Niels Bohr's predictable atom model.

Strategy: Standard debugging. All other methods apply.
How to confirm: Run it 10 times. Fails 10 times? Bohrbug.
```

### Heisenbug — The Quantum Bug
```
Definition: Disappears or changes behavior when you try to observe or debug it.
Named after Heisenberg's Uncertainty Principle.
Common causes:
  - Race condition where debugger breakpoint changes timing
  - Uninitialized variable (different value in debug vs release)
  - Debug build vs optimized build behavior difference
  - Observation adds overhead that changes race condition outcome
  - Logging itself changes timing enough to hide the bug

Strategy:
  1. NEVER use breakpoints — they change timing and hide the bug
  2. Use non-invasive logging only (no pausing execution)
  3. Use production-identical build settings (no debug flags)
  4. Run under production load (not just one request)
  5. Run tests 100+ times in parallel to find the race condition
  6. Enable verbose logging and look for the pattern in failures
  7. Focus on: shared mutable state, async timing, init order, memory

Signs: "Works fine when I debug it", "Only fails in production",
       "Fails randomly", "Can't reproduce it anymore"
```

### Mandelbug — The Fractal Bug
```
Definition: Fixing one thing reveals more bugs. Chaotic behavior.
Named after Mandelbrot's fractal geometry (self-similarity).
Causes:
  - System grown organically over years without design
  - Number of possible states is astronomical
  - Multiple interacting subsystems with no clear ownership
  - Technical debt compounding to the point of instability

Strategy:
  1. STOP fixing individual symptoms — you will not win this way
  2. Map the full system architecture and dependency graph
  3. Find the architectural flaw (not the code flaw)
  4. Often: a well-placed abstraction layer eliminates the whole class
  5. A workaround may be more appropriate than a deep fix
  6. Recommend: dedicated refactoring sprint, not hotfix

Signs: "Every fix breaks something else", "The more I dig, the worse it gets",
       "We've been fighting this for months"
```

### Schroedinbug — The Observed Bug
```
Definition: Code that should never have worked, but did — until someone noticed.
Named after Schrödinger's cat (superposition collapses on observation).
Causes:
  - Code relied on undefined behavior that happened to work
  - Lucky memory layout or initialization order
  - Compensating bugs that cancelled each other out
  - Works until conditions change (load, data volume, version upgrade)

Strategy:
  1. Do NOT try to preserve the old behavior — it was wrong
  2. Rewrite the section correctly from first principles
  3. The fix is: implement it the right way, not a patch
  4. Add tests that would have caught this originally

Signs: "I was reading the code and realized it can't possibly work",
       "It worked before we upgraded", "Worked for small data, fails for large"
```

---

## METHOD 3 — 5 WHYS (Toyota/Google SRE — Find the Real Root Cause)

Developed by Sakichi Toyoda for Toyota. Adopted by Google SRE.
Forces you past the symptom to the systemic cause.

```
The 5 Whys process:
Ask "Why?" 5 times. Each answer becomes the subject of the next "Why?"
The 5th Why reveals a systemic cause — usually a process, design, or knowledge gap.

Rules:
- Don't accept a surface answer. Push deeper.
- Each "why" must be proven, not assumed.
- Stop when you reach something you can actually fix permanently.
- Multiple branches are valid (one event can have multiple causes).

Example from real production bug:
Why 1: Why is the API returning 500?
        → The database query is timing out

Why 2: Why is the query timing out?
        → The query is scanning 10M rows without an index

Why 3: Why is there no index?
        → The index was dropped in a migration 3 weeks ago

Why 4: Why wasn't the dropped index caught?
        → The migration was not reviewed for performance impact

Why 5: Why wasn't performance reviewed?
        → ROOT CAUSE: No performance review checklist in migration process

Fix: Add index (immediate). Add performance checklist to migration process (permanent).
```

---

## METHOD 4 — FISHBONE / ISHIKAWA DIAGRAM (For Complex Multi-Factor Bugs)

Use when: bug has multiple possible causes, team is stuck, or postmortem is needed.
Categorizes all potential causes systematically.

```
Structure: Spine = The problem
           Bones = Categories of causes (adapt for software)

Software categories:
  PEOPLE:      Who did what? Training gaps? Assumptions made?
  PROCESS:     What process was followed? What was skipped?
  TECHNOLOGY:  Version? Dependency? Framework behavior? Platform?
  ENVIRONMENT: Dev vs prod? Config? Infrastructure? Load?
  DATA:        Input format? Volume? Encoding? Edge case?
  CODE:        Logic error? Race condition? Integration point?

For each category, list ALL possible causes.
Then test each hypothesis to eliminate or confirm.
The last remaining confirmed cause = root cause.

When to use: Mandelbug, multi-factor incidents, team postmortems
```

---

## METHOD 5 — FAULT TREE ANALYSIS (Map All Failure Paths)

Use when: Critical system, multiple failure paths possible, postmortem.

```
Start from the failure (top) and work DOWN to causes.
Each node is: a failure event
Each branch is: AND (all conditions needed) or OR (any condition sufficient)

AND gate: All child events must happen for parent to happen
OR gate: Any child event causes the parent

Example:
                   [Login Fails]
                   /            \
            [Server Error]    [Auth Error]
               /    \              |
        [DB Down]  [Timeout]  [Token Invalid]
                                   |
                             [Clock Skew]

This shows: Login can fail via multiple independent paths.
Fixing one path (server error) does not fix auth errors.
Both paths must be fixed for the top-level failure to stop.
```

---

## METHOD 6 — GOOGLE SRE POSTMORTEM METHODOLOGY

For bugs that caused production incidents:

```
Timeline construction (build this immediately):
  [exact timestamp]: [what happened]
  [exact timestamp]: [who noticed / who did what]
  [exact timestamp]: [what was tried]
  [exact timestamp]: [resolution]

Blameless principle:
  "How did the system allow this failure to happen?"
  NOT: "Who made this mistake?"
  
  Blame hides information. Blameless postmortems surface it.
  People tell you what really happened when they don't fear punishment.

5 elements of a complete postmortem:
  1. Summary and impact (what broke, for how long, how many affected)
  2. Timeline (sequence of events, including discovery and response)
  3. Root cause (from 5 Whys — systemic, not superficial)
  4. Contributing factors (median = 3.5 per incident)
  5. Action items with owners and deadlines (prevent recurrence)

Minimum viable postmortem for any bug taking > 1 hour:
  ROOT CAUSE (from 5 Whys):
  WHAT WOULD HAVE CAUGHT THIS EARLIER:
  WHAT PREVENTS RECURRENCE:
  REGRESSION TEST TO ADD:
```

---

## METHOD 7 — CHAOS ENGINEERING / HYPOTHESIS TESTING

For bugs that are intermittent or hard to reproduce:

```
Hypothesis testing framework:
  1. Form a SPECIFIC hypothesis: "I believe X causes Y under condition Z"
  2. Design experiment to prove or disprove (NOT to fix)
  3. Run experiment. Observe. Document.
  4. If disproved: form new hypothesis
  5. If proved: NOW fix it (and verify fix under same conditions)

Never fix before proving the hypothesis.
A fix that doesn't address the confirmed cause is a guess.

Chaos injection for intermittent bugs:
  Add artificial delay at suspected timing gap → does it reproduce?
  Add artificial load → does it reproduce?
  Starve resource (memory, connections) → does it reproduce?
  Force specific execution order → does it reproduce?
  If YES to any: you've found the uncontrolled condition.
```

---

## KEY INSIGHTS FROM RESEARCH

1. **Developers with structured debugging strategies resolve issues 40–60% faster** than those who approach problems reactively.

2. **The part of the system you don't understand is where the bug is.** Not Murphy's Law — if you didn't understand it when designing, you likely got it wrong.

3. **Stimulate, don't simulate.** A bug reproduced with fake conditions is not the real bug. The fix will not hold.

4. **The median production incident has 3.5 contributing factors.** Fixing one factor may not fix the bug.

5. **"If you didn't fix it, it ain't fixed."** The bug must fail under old conditions and not fail after the fix — under identical conditions.

6. **Heisenbugs are the hardest.** The debugger IS the problem. Use non-invasive logging only. Production timing only.

7. **Mandelbugs require architecture changes, not code patches.** You cannot hotfix your way out of fractal complexity.

8. **The 5th Why is always a process/design failure.** Code bugs have code fixes. Root causes have process fixes. Both must be addressed.
