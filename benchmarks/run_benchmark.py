#!/usr/bin/env python3
"""
nuclear-bug-fix benchmark runner
Usage: ANTHROPIC_API_KEY=sk-... python3 benchmarks/run_benchmark.py [--cases BE-001,FE-002] [--from-id 21]
"""

import os, sys, json, time, re, argparse
from pathlib import Path
import urllib.request, urllib.error

REPO = Path(__file__).parent.parent
CASES_DIR = REPO / "benchmarks" / "cases"
RESULTS_DIR = REPO / "benchmarks" / "results"
SKILL_MD = REPO / "SKILL.md"

SCORING_MODEL = "claude-haiku-4-5-20251001"   # scorer (cheap + fast)
SUBJECT_MODEL = "claude-sonnet-4-6"            # model being benchmarked

SYSTEM_PROMPT_TEMPLATE = """You are running the nuclear-bug-fix skill. 
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
Score this response. Return ONLY a JSON object with:
{{
  "score": <integer 0-100>,
  "breakdown": {{"first_shot": <0-40>, "root_cause": <0-25>, "fix": <0-20>, "verification": <0-10>, "evidence": <0-5>}},
  "penalties": <integer, negative or 0>,
  "verdict": "PASS|PARTIAL|FAIL",
  "notes": "<one sentence explaining the main strength or weakness>"
}}
"""

def api_call(model, system, user, api_key, max_tokens=4000, retries=3):
    for attempt in range(retries):
        try:
            payload = json.dumps({
                "model": model,
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}]
            }).encode()
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())["content"][0]["text"]
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"  Retry {attempt+1}/{retries} after error: {e}")
            time.sleep(5 * (attempt + 1))

def score_response(evaluator_md, response, api_key):
    prompt = SCORER_PROMPT.format(evaluator_md=evaluator_md, response=response[:6000])
    raw = api_call(SCORING_MODEL, "You are a precise benchmark scorer. Return only valid JSON.", prompt, api_key, max_tokens=500)
    # Extract JSON from response
    match = re.search(r'\{.*\}', raw, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError(f"Could not parse scorer JSON: {raw[:200]}")

def run_case(case_id, skill_system, api_key):
    case_dir = CASES_DIR / case_id
    prompt_md = (case_dir / "prompt.md").read_text()
    evaluator_md = (case_dir / "evaluator.md").read_text()

    # Get skill response
    response = api_call(SUBJECT_MODEL, skill_system, prompt_md, api_key)
    
    # Score it
    result = score_response(evaluator_md, response, api_key)
    result["case_id"] = case_id
    result["response_preview"] = response[:300]
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", help="Comma-separated case IDs to run")
    parser.add_argument("--from-id", type=int, default=1, help="Start from case number (skip already scored)")
    parser.add_argument("--track", help="Filter by track name")
    parser.add_argument("--limit", type=int, default=100, help="Max cases to run")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    skill_system = SYSTEM_PROMPT_TEMPLATE.format(skill_md=SKILL_MD.read_text())

    # Determine which cases to run
    if args.cases:
        case_ids = [c.strip() for c in args.cases.split(",")]
    else:
        all_cases = sorted(CASES_DIR.iterdir())
        case_ids = [c.name for c in all_cases if c.is_dir()]

    # Filter by track if requested
    if args.track:
        filtered = []
        for cid in case_ids:
            ev = (CASES_DIR / cid / "evaluator.md").read_text()
            if f"track: {args.track}" in ev:
                filtered.append(cid)
        case_ids = filtered

    case_ids = case_ids[:args.limit]
    print(f"Running {len(case_ids)} cases...\n")

    results = []
    for i, case_id in enumerate(case_ids, 1):
        print(f"[{i:3d}/{len(case_ids)}] {case_id}...", end=" ", flush=True)
        try:
            result = run_case(case_id, skill_system, api_key)
            results.append(result)
            verdict_icon = "✅" if result["verdict"] == "PASS" else ("⚠️" if result["verdict"] == "PARTIAL" else "❌")
            print(f"{verdict_icon} {result['score']:3d}/100 — {result['notes'][:60]}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
            results.append({"case_id": case_id, "score": 0, "verdict": "ERROR", "notes": str(e)[:100]})
        time.sleep(1)  # Rate limit buffer

    # Write results
    RESULTS_DIR.mkdir(exist_ok=True)
    scores = [r["score"] for r in results if isinstance(r.get("score"), int)]
    mean = sum(scores) / len(scores) if scores else 0

    output_file = RESULTS_DIR / "iteration-2-scores.md"
    lines = [
        "# Benchmark Results — Iteration 2\n",
        f"Run against {len(results)} cases. Scored by {SCORING_MODEL}.\n\n",
        f"**Mean: {mean:.1f}/100 | PASS: {sum(1 for r in results if r.get('verdict')=='PASS')} | PARTIAL: {sum(1 for r in results if r.get('verdict')=='PARTIAL')} | FAIL: {sum(1 for r in results if r.get('verdict')=='FAIL')}**\n\n",
        "## Scores\n\n",
        "| Case | Score | Verdict | Notes |\n",
        "|---|---:|---:|---|\n"
    ]
    for r in sorted(results, key=lambda x: x.get("score", 0)):
        vid = r.get("verdict", "?")
        icon = "✅" if vid == "PASS" else ("⚠️" if vid == "PARTIAL" else "❌")
        lines.append(f"| {r['case_id']} | {r.get('score',0)} | {icon} {vid} | {r.get('notes','')[:80]} |\n")

    output_file.write_text("".join(lines))
    print(f"\n✅ Results written to {output_file}")
    print(f"Mean score: {mean:.1f}/100")

    # Save raw JSON too
    (RESULTS_DIR / "iteration-2-raw.json").write_text(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
