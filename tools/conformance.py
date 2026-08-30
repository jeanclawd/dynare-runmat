#!/usr/bin/env python3
"""Semantic conformance harness: does RunMat *behave* like MATLAB?

The parse sweep answers "can RunMat read Dynare". This answers the harder
question: for the language features Dynare actually leans on, does RunMat
produce MATLAB's answer?

Each test is a `.m` file under tests/conformance/<category>/ with a sibling
`.expected` holding the exact stdout MATLAB produces. A test passes only if
RunMat's stdout matches after whitespace normalization.

Tests may be marked with a leading `%% xfail: <reason>` comment — a known gap,
recorded so a regression (or a fix) is visible rather than silently tolerated.

Usage:
    tools/conformance.py --suite tests/conformance --out reports/conformance
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter, defaultdict

NOISE = re.compile(r"wgpu|libEGL|DRI2|No config found|No windowing system|WARN")
XFAIL = re.compile(r"^%%\s*xfail:\s*(.*)$", re.M)


def clean(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if not NOISE.search(ln)]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    # Collapse runs of internal whitespace so numeric column padding does not
    # decide a pass/fail on its own.
    return "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in lines)


def run_case(runmat: str, path: str, timeout: int):
    try:
        proc = subprocess.run(
            [runmat, "run", path], capture_output=True, text=True, timeout=timeout
        )
        return proc.stdout, proc.stderr, proc.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -9


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runmat", default="runmat")
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--filter", default="", help="substring filter on test id")
    args = ap.parse_args()

    suite = os.path.abspath(args.suite)
    cases = []
    for dirpath, _d, filenames in os.walk(suite):
        for fn in sorted(filenames):
            if fn.endswith(".m"):
                cases.append(os.path.join(dirpath, fn))
    cases.sort()
    if args.filter:
        cases = [c for c in cases if args.filter in c]

    results = []
    by_cat = defaultdict(Counter)
    started = time.time()

    for path in cases:
        rel = os.path.relpath(path, suite)
        category = rel.split(os.sep)[0] if os.sep in rel else "misc"
        test_id = os.path.splitext(rel)[0].replace(os.sep, "/")

        with open(path, "r", errors="replace") as fh:
            src = fh.read()
        xf = XFAIL.search(src)
        xfail_reason = xf.group(1).strip() if xf else None

        exp_path = os.path.splitext(path)[0] + ".expected"
        if not os.path.exists(exp_path):
            results.append({"id": test_id, "category": category,
                            "status": "no_expected"})
            by_cat[category]["no_expected"] += 1
            continue
        with open(exp_path, "r", errors="replace") as fh:
            expected = clean(fh.read())

        out, err, rc = run_case(args.runmat, path, args.timeout)
        actual = clean(out)
        matched = actual == expected

        if matched:
            status = "xpass" if xfail_reason else "pass"
        else:
            status = "xfail" if xfail_reason else "fail"

        entry = {
            "id": test_id,
            "category": category,
            "status": status,
            "expected": expected,
            "actual": actual,
            "returncode": rc,
        }
        if not matched:
            entry["stderr"] = clean(err)[:600]
        if xfail_reason:
            entry["xfail_reason"] = xfail_reason
        results.append(entry)
        by_cat[category][status] += 1

    totals = Counter(r["status"] for r in results)
    n = len(results)
    # xpass counts as working; xfail is a known, tracked gap.
    working = totals["pass"] + totals["xpass"]

    payload = {
        "suite": suite,
        "total": n,
        "totals": dict(totals),
        "working": working,
        "conformance_pct": round(100.0 * working / n, 2) if n else 0.0,
        "by_category": {k: dict(v) for k, v in sorted(by_cat.items())},
        "results": results,
        "elapsed_sec": round(time.time() - started, 1),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as fh:
        json.dump(payload, fh, indent=2)

    with open(args.out + ".md", "w") as fh:
        fh.write("# RunMat semantic conformance (Dynare-relevant features)\n\n")
        fh.write(f"- Cases: **{n}**\n")
        fh.write(f"- Working (pass + xpass): **{working}** "
                 f"({payload['conformance_pct']}%)\n")
        fh.write(f"- Failing: **{totals['fail']}**, "
                 f"known gaps (xfail): **{totals['xfail']}**\n\n")
        fh.write("## By category\n\n")
        for cat, counts in payload["by_category"].items():
            tot = sum(counts.values())
            ok = counts.get("pass", 0) + counts.get("xpass", 0)
            fh.write(f"### {cat} — {ok}/{tot}\n\n")
            for r in results:
                if r["category"] != cat or r["status"] in ("pass",):
                    continue
                mark = {"fail": "❌", "xfail": "⚠️", "xpass": "🎉",
                        "no_expected": "❔"}.get(r["status"], "?")
                note = r.get("xfail_reason") or ""
                fh.write(f"- {mark} `{r['id']}` {note}\n")
            fh.write("\n")

    print(json.dumps({k: payload[k] for k in
                      ("total", "totals", "conformance_pct", "elapsed_sec")},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
