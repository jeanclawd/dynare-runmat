#!/usr/bin/env python3
"""Break a parse sweep down by Dynare subsystem.

A single repository-wide percentage hides the thing you actually want to know
when planning work: *which parts* of Dynare are closest to running. Dynare's
`matlab/` tree is organised by subsystem — `estimation/`, `kalman/`,
`optimization/`, `+occbin/`, `@dprior/` and so on — so grouping by top-level
directory says where the remaining work is concentrated.

Usage:
    tools/subsystem_report.py reports/parse_sweep_shimmed.json
    tools/subsystem_report.py reports/parse_sweep_shimmed.json --min-files 5
"""

import argparse
import collections
import json
import sys


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sweep", help="a parse_sweep JSON report")
    ap.add_argument("--min-files", type=int, default=8,
                    help="ignore directories with fewer files than this")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args()

    with open(args.sweep) as fh:
        data = json.load(fh)

    counts = collections.defaultdict(lambda: {"clean": 0, "total": 0})
    reasons = collections.defaultdict(collections.Counter)
    for entry in data["results"]:
        path = entry["file"]
        top = path.split("/")[0] if "/" in path else "(root)"
        counts[top]["total"] += 1
        if entry.get("ok"):
            counts[top]["clean"] += 1
        else:
            reasons[top][(entry.get("message") or "")[:60]] += 1

    rows = [
        (name, c["clean"], c["total"], 100.0 * c["clean"] / c["total"])
        for name, c in counts.items()
        if c["total"] >= args.min_files
    ]
    rows.sort(key=lambda r: -r[3])

    if args.markdown:
        print("# Dynare subsystems by RunMat parse rate\n")
        print(f"Source: `{args.sweep}`. Directories with at least "
              f"{args.min_files} files.\n")
        print("| Subsystem | Clean | Files | Rate | Most common blocker |")
        print("| --- | ---: | ---: | ---: | --- |")
        for name, clean, total, pct in rows:
            top_reason = reasons[name].most_common(1)
            blocker = top_reason[0][0] if top_reason else "—"
            print(f"| `{name}` | {clean} | {total} | {pct:.0f}% | {blocker} |")
    else:
        print(f"{'subsystem':<34}{'clean':>7}{'total':>7}{'rate':>8}")
        for name, clean, total, pct in rows:
            print(f"{name:<34}{clean:>7}{total:>7}{pct:>7.0f}%")

    return 0


if __name__ == "__main__":
    sys.exit(main())
