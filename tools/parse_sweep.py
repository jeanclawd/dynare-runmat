#!/usr/bin/env python3
"""Run `runmat check` over every .m file in a tree and classify the failures.

This is the broad-signal pass: it answers "how much of Dynare can RunMat even
parse?" without needing a model to solve. Semantic conformance is a separate
harness (conformance.py).

Usage:
    tools/parse_sweep.py --root ../dynare-upstream --out reports/parse_sweep
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from collections import Counter

# `runmat check` writes GPU/EGL probe noise to stderr on headless boxes.
NOISE = re.compile(r"wgpu|libEGL|DRI2|No config found|No windowing system")

# Error-id -> short human label. Anything unmatched is bucketed by its raw id.
ERROR_ID = re.compile(r"error\[([A-Za-z0-9_:]+)\]")
SUMMARY = re.compile(r"checked .*?: (\d+) error\(s\), (\d+) warning\(s\)")


def classify(stdout: str, stderr: str) -> tuple[str, str]:
    """Return (bucket, first_message) for a failing check."""
    text = "\n".join(
        ln for ln in (stdout + "\n" + stderr).splitlines() if not NOISE.search(ln)
    )
    ids = ERROR_ID.findall(text)
    bucket = ids[0] if ids else "Unknown"

    # Pull the human-readable part of the first error line for sub-bucketing.
    msg = ""
    for ln in text.splitlines():
        m = re.match(r"error\[[^\]]+\]:\s*(.*)", ln)
        if m:
            msg = m.group(1).strip()
            break
        if ln.startswith("error:"):
            msg = ln[len("error:"):].strip()
            break
    return bucket, msg


def normalize(msg: str) -> str:
    """Collapse a message to a stable signature so counts group sensibly."""
    msg = re.sub(r"'[^']*'", "'X'", msg)
    msg = re.sub(r"\b\d+\b", "N", msg)
    return msg[:100]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="tree to sweep")
    ap.add_argument("--out", required=True, help="output path prefix")
    ap.add_argument("--runmat", default="runmat")
    ap.add_argument("--limit", type=int, default=0, help="stop after N files (debug)")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    files = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if fn.endswith(".m"):
                files.append(os.path.join(dirpath, fn))
    files.sort()
    if args.limit:
        files = files[: args.limit]

    results = []
    buckets = Counter()
    signatures = Counter()
    started = time.time()

    for i, path in enumerate(files, 1):
        try:
            proc = subprocess.run(
                [args.runmat, "check", path],
                capture_output=True,
                text=True,
                timeout=60,
            )
            out, err, rc = proc.stdout, proc.stderr, proc.returncode
        except subprocess.TimeoutExpired:
            out, err, rc = "", "TIMEOUT", -9

        combined = out + "\n" + err
        m = SUMMARY.search(combined)
        n_err = int(m.group(1)) if m else (0 if rc == 0 and "error" not in combined else 1)
        ok = n_err == 0 and rc == 0

        rel = os.path.relpath(path, root)
        entry = {"file": rel, "ok": ok, "errors": n_err}
        if not ok:
            bucket, msg = classify(out, err)
            sig = normalize(msg)
            entry["bucket"] = bucket
            entry["message"] = msg
            buckets[bucket] += 1
            signatures[f"{bucket} | {sig}"] += 1
        results.append(entry)

        if i % 100 == 0 or i == len(files):
            rate = i / max(time.time() - started, 1e-9)
            print(
                f"  {i}/{len(files)} files  ({rate:.1f}/s)",
                file=sys.stderr,
                flush=True,
            )

    n_ok = sum(1 for r in results if r["ok"])
    total = len(results)
    payload = {
        "root": root,
        "total": total,
        "parsed_ok": n_ok,
        "failed": total - n_ok,
        "pass_rate": round(100.0 * n_ok / total, 2) if total else 0.0,
        "buckets": buckets.most_common(),
        "signatures": signatures.most_common(40),
        "results": results,
        "elapsed_sec": round(time.time() - started, 1),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as fh:
        json.dump(payload, fh, indent=2)

    with open(args.out + ".md", "w") as fh:
        fh.write("# RunMat parse sweep over Dynare\n\n")
        fh.write(f"- Files scanned: **{total}**\n")
        fh.write(f"- Parsed clean: **{n_ok}** ({payload['pass_rate']}%)\n")
        fh.write(f"- Failed: **{total - n_ok}**\n\n")
        fh.write("## Failures by error id\n\n")
        for b, c in buckets.most_common():
            fh.write(f"- `{b}` — {c}\n")
        fh.write("\n## Top failure signatures\n\n")
        for s, c in signatures.most_common(25):
            fh.write(f"- {c} x — {s}\n")

    print(json.dumps({k: payload[k] for k in
                      ("total", "parsed_ok", "failed", "pass_rate", "elapsed_sec")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
