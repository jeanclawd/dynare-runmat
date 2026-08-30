#!/usr/bin/env python3
"""Track code that MATLAB accepts but `runmat check` rejects.

The runtime conformance suite runs code and compares output. It cannot see the
largest class of Dynare failures, because those files never get as far as
running: `runmat check` refuses them statically, over rules MATLAB does not
have — definite assignment, `global` not being recognised as bringing a name
into scope, and brace indexing of a value it cannot prove is a cell.

Each case here is valid MATLAB that *should* check clean. A case may carry
`%% xfail-check: <reason>` for a gap already confirmed, so the suite stays
green today and a fix surfaces as `xpass`.

Where a case is also runnable, it carries `%% runs: <expected stdout>` and the
harness executes it. A case that checks-rejected but runs correctly is the
interesting one: the checker is refusing something the runtime handles. A case
that fails both is a genuine runtime gap, and the report says which it is.

Usage:
    tools/check_conformance.py --suite tests/check --out reports/check_conformance
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

NOISE = re.compile(r"wgpu|libEGL|DRI2|No config found|No windowing system|WARN")
XFAIL = re.compile(r"^%%\s*xfail-check:\s*(.*)$", re.M)
RUNS = re.compile(r"^%%\s*runs:\s*(.*)$", re.M)
SUMMARY = re.compile(r"checked .*?: (\d+) error\(s\)")


def clean(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if not NOISE.search(ln)]
    return "\n".join(ln.strip() for ln in lines if ln.strip())


def run(cmd, cwd, timeout):
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                           timeout=timeout)
        return p.stdout, p.stderr, p.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -9


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--runmat", default="runmat")
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    suite = os.path.abspath(args.suite)
    cases = sorted(
        os.path.join(d, f)
        for d, _s, fs in os.walk(suite)
        for f in fs
        if f.endswith(".m") and not f.startswith("driver_")
    )

    results = []
    started = time.time()

    for path in cases:
        rel = os.path.relpath(path, suite)
        with open(path, errors="replace") as fh:
            src = fh.read()
        xf = XFAIL.search(src)
        reason = xf.group(1).strip() if xf else None
        runs = RUNS.search(src)
        expected_stdout = runs.group(1).strip() if runs else None

        out, err, _rc = run([args.runmat, "check", path], os.path.dirname(path),
                            args.timeout)
        combined = clean(out + "\n" + err)
        m = SUMMARY.search(combined)
        n_err = int(m.group(1)) if m else (1 if "error" in combined else 0)
        checks_clean = n_err == 0

        entry = {"id": os.path.splitext(rel)[0].replace(os.sep, "/"),
                 "checks_clean": checks_clean, "errors": n_err}
        if not checks_clean:
            first = next((ln for ln in combined.splitlines()
                          if ln.startswith("error")), "")
            entry["error"] = first[:200]

        # If the case says it runs, prove it — that is the evidence that the
        # checker is wrong rather than the code.
        if expected_stdout is not None:
            drv = os.path.join(os.path.dirname(path),
                               "driver_" + os.path.basename(path))
            if os.path.exists(drv):
                rout, _rerr, _rc2 = run([args.runmat, "run",
                                         os.path.basename(drv)],
                                        os.path.dirname(path), args.timeout)
            else:
                rout, _rerr, _rc2 = run([args.runmat, "run", path],
                                        os.path.dirname(path), args.timeout)
            actual = clean(rout)
            entry["runs_correctly"] = actual == expected_stdout
            entry["run_expected"] = expected_stdout
            entry["run_actual"] = actual

        if checks_clean:
            entry["status"] = "xpass" if reason else "pass"
        else:
            entry["status"] = "xfail" if reason else "fail"
        if reason:
            entry["xfail_reason"] = reason
        results.append(entry)

    totals = Counter(r["status"] for r in results)
    n = len(results)
    payload = {
        "suite": suite,
        "total": n,
        "totals": dict(totals),
        "elapsed_sec": round(time.time() - started, 1),
        "results": results,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as fh:
        json.dump(payload, fh, indent=2)

    with open(args.out + ".md", "w") as fh:
        fh.write("# Valid MATLAB that `runmat check` rejects\n\n")
        fh.write("Every case here is legal MATLAB. `runs correctly: True` "
                 "means the code executes and returns MATLAB's answer, so the "
                 "rejection is the checker's and not the code's. "
                 "`False` means the gap is in the runtime too, not only in "
                 "`runmat check`.\n\n")
        fh.write(f"- Cases: **{n}**\n")
        fh.write(f"- Check clean: **{totals['pass'] + totals['xpass']}**\n")
        fh.write(f"- Known checker gaps (xfail): **{totals['xfail']}**\n")
        fh.write(f"- Unexpected: **{totals['fail']}**\n\n")
        for r in results:
            mark = {"pass": "✅", "xfail": "⚠️", "xpass": "🎉",
                    "fail": "❌"}.get(r["status"], "?")
            fh.write(f"### {mark} `{r['id']}`\n\n")
            if r.get("xfail_reason"):
                fh.write(f"- gap: {r['xfail_reason']}\n")
            if r.get("error"):
                fh.write(f"- `{r['error']}`\n")
            if "runs_correctly" in r:
                fh.write(f"- runs correctly: **{r['runs_correctly']}** "
                         f"(expected `{r['run_expected']}`, "
                         f"got `{r['run_actual']}`)\n")
            fh.write("\n")

    print(json.dumps({k: payload[k] for k in ("total", "totals", "elapsed_sec")},
                     indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
