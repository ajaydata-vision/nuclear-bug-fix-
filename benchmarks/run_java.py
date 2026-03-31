#!/usr/bin/env python3
"""
nuclear-bug-fix benchmark runner — extended
Usage:
  ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_java.py              # all JV/WF/OR/JT cases
  ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_java.py --adversarial # JV-A cases only (baseline)
  ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_java.py --all         # full 127-case suite
"""

import os, sys, json, time, re, argparse
from pathlib import Path
from datetime import datetime

REPO       = Path(__file__).parent.parent
CASES_DIR  = REPO / "benchmarks" / "cases"
RESULTS_DIR= REPO / "benchmarks" / "results"
SKILL_MD   = REPO / "SKILL.md"

SUBJECT_MODEL = "claude-sonnet-4-6"
SCORER_MODEL  = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """You are running the nuclear-bug-fix skill.
Below is the full skill methodology. Apply it precisely when responding.

---
{skill_md}
---

When given a bug report, run the full methodology: intake, triage, diagnosis, DDx Gate, verdict with BEFORE/AFTER code."""

SCORER_PROMPT = """You are scoring a response from an AI bug-fixing skill against a ground truth evaluator.

## SCORING RUBRIC (100 points total)
- 40 pts: First-shot resolution (correct root cause + fix in first response, no iteration needed)
- 25 pts: Root cause accuracy (correctly identifies the specific root cause)
- 20 pts: Fix accuracy (fix is correct and complete)
- 10 pts: Verification quality (provides concrete verification steps)
- 5 pts:  Evidence discipline (does not assert without evidence, uses logs/proofs)

## PENALTIES
- -40: Confident wrong answer on root cause
- -25: Root cause mismatch with ground truth
- -20: Shotgun rewrite (rewrites entire file instead of targeted fix)
- -15: No verification steps provided
- -10: Revisits a path explicitly marked as already tried

## GROUND TRUTH
{evaluator_md}

## SKILL RESPONSE TO SCORE
{response}

## YOUR TASK
Score this response. Return ONLY valid JSON:
{{
  "score": <integer 0-100>,
  "breakdown": {{"first_shot": <0-40>, "root_cause": <0-25>, "fix": <0-20>, "verification": <0-10>, "evidence": <0-5>}},
  "penalties": <integer 0 or negative>,
  "verdict": "PASS|PARTIAL|FAIL",
  "notes": "<one sentence — main strength or weakness>"
}}"""

import urllib.request, urllib.error

def call_api(model, system, user, key, max_tokens=4000, retries=3):
    for attempt in range(retries):
        try:
            payload = json.dumps({
                "model": model, "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages", data=payload,
                headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())["content"][0]["text"]
        except Exception as e:
            if attempt == retries - 1: raise
            wait = 10 * (attempt + 1)
            print(f"    ↻ retry {attempt+1} in {wait}s ({e})")
            time.sleep(wait)

def run_case(case_id, skill_system, key):
    d = CASES_DIR / case_id
    prompt    = (d / "prompt.md").read_text()
    evaluator = (d / "evaluator.md").read_text()

    response = call_api(SUBJECT_MODEL, skill_system, prompt, key)
    raw = call_api(SCORER_MODEL,
                   "You are a precise benchmark scorer. Return only valid JSON.",
                   SCORER_PROMPT.format(evaluator_md=evaluator, response=response[:6000]),
                   key, max_tokens=500)
    m = re.search(r'\{.*\}', raw, re.DOTALL)
    if not m: raise ValueError(f"Bad scorer JSON: {raw[:200]}")
    result = json.loads(m.group())
    result["case_id"] = case_id
    result["response_snippet"] = response[:400]
    return result

def write_results(results, label):
    RESULTS_DIR.mkdir(exist_ok=True)
    scores = [r["score"] for r in results if isinstance(r.get("score"), int)]
    mean   = sum(scores) / len(scores) if scores else 0
    passing = sum(1 for r in results if r.get("verdict") == "PASS")
    partial  = sum(1 for r in results if r.get("verdict") == "PARTIAL")
    failing  = sum(1 for r in results if r.get("verdict") == "FAIL")

    ts   = datetime.now().strftime("%Y-%m-%d %H:%M")
    slug = label.lower().replace(" ", "-")
    md_path  = RESULTS_DIR / f"{slug}.md"
    json_path= RESULTS_DIR / f"{slug}.json"

    lines = [
        f"# Benchmark Results — {label}\n\n",
        f"*Run: {ts} | Model: {SUBJECT_MODEL} | Scorer: {SCORER_MODEL}*\n\n",
        f"**Mean: {mean:.1f}/100 | PASS: {passing} | PARTIAL: {partial} | FAIL: {failing} | n={len(results)}**\n\n",
        "## Scores By Case\n\n",
        "| Case | Score | Verdict | Notes |\n",
        "|---|---:|---|---|\n"
    ]
    for r in sorted(results, key=lambda x: x.get("score", 0)):
        v    = r.get("verdict", "?")
        icon = "✅" if v == "PASS" else ("⚠️" if v == "PARTIAL" else "❌")
        note = r.get("notes", "")[:80]
        lines.append(f"| {r['case_id']} | {r.get('score',0)} | {icon} {v} | {note} |\n")

    # Track breakdown
    tracks = {}
    for r in results:
        ev_path = CASES_DIR / r["case_id"] / "evaluator.md"
        if ev_path.exists():
            for line in ev_path.read_text().splitlines():
                if line.startswith("- track:"):
                    track = line.split(":", 1)[1].strip()
                    tracks.setdefault(track, []).append(r.get("score", 0))
    if tracks:
        lines += ["\n## Scores By Track\n\n", "| Track | n | Mean |\n", "|---|---:|---:|\n"]
        for t, ss in sorted(tracks.items()):
            lines.append(f"| {t} | {len(ss)} | {sum(ss)/len(ss):.1f} |\n")

    md_path.write_text("".join(lines))
    json_path.write_text(json.dumps(results, indent=2))
    return mean, md_path

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--adversarial", action="store_true", help="Run only JV-A01..A05 (baseline)")
    p.add_argument("--java",        action="store_true", help="Run all java-enterprise cases (default)")
    p.add_argument("--all",         action="store_true", help="Run full 127-case suite")
    p.add_argument("--cases",       help="Specific comma-separated case IDs")
    args = p.parse_args()

    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        print("ERROR: ANTHROPIC_API_KEY not set\n"
              "Run: ANTHROPIC_API_KEY=sk-ant-... python3 benchmarks/run_java.py")
        sys.exit(1)

    # Select cases
    if args.cases:
        case_ids = [c.strip() for c in args.cases.split(",")]
        label = "Custom Selection"
    elif args.adversarial:
        case_ids = ["JV-A01", "JV-A02", "JV-A03", "JV-A04", "JV-A05"]
        label = "Java Adversarial Baseline"
    elif args.all:
        case_ids = sorted(d.name for d in CASES_DIR.iterdir() if d.is_dir())
        label = "Full Suite"
    else:  # default: all java-enterprise cases
        java_prefixes = ("JV-", "WF-", "OR-", "JT-")
        case_ids = sorted(
            d.name for d in CASES_DIR.iterdir()
            if d.is_dir() and any(d.name.startswith(p) for p in java_prefixes)
        )
        label = "Java Enterprise"

    skill_system = SYSTEM_PROMPT.format(skill_md=SKILL_MD.read_text())
    total = len(case_ids)
    print(f"\n{'='*60}")
    print(f"  nuclear-bug-fix benchmark — {label}")
    print(f"  {total} cases | subject={SUBJECT_MODEL}")
    print(f"{'='*60}\n")

    results = []
    for i, cid in enumerate(case_ids, 1):
        print(f"[{i:3d}/{total}] {cid:<12}", end=" ", flush=True)
        try:
            r = run_case(cid, skill_system, key)
            results.append(r)
            v    = r.get("verdict", "?")
            icon = "✅" if v == "PASS" else ("⚠️" if v == "PARTIAL" else "❌")
            print(f"{icon} {r['score']:3d}/100  {r.get('notes','')[:55]}")
        except Exception as e:
            results.append({"case_id": cid, "score": 0, "verdict": "ERROR", "notes": str(e)[:100]})
            print(f"❌ ERROR: {e}")
        time.sleep(1.5)  # gentle rate-limit buffer

    mean, out = write_results(results, label)
    scores = [r["score"] for r in results if isinstance(r.get("score"), int)]

    print(f"\n{'='*60}")
    print(f"  RESULTS — {label}")
    print(f"  Mean:    {mean:.1f}/100")
    print(f"  High(85+): {sum(1 for s in scores if s>=85)}/{len(scores)}")
    print(f"  Pass(100): {sum(1 for s in scores if s==100)}/{len(scores)}")
    print(f"  Written: {out}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
