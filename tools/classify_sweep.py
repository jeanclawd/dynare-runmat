#!/usr/bin/env python3
"""Sort parse-sweep failures into tiers by what they actually mean.

`runmat check` reports two very different kinds of problem under one exit code,
and conflating them makes RunMat look worse than it is:

  * **Syntax** — RunMat cannot read the file. A real incompatibility.
  * **Static analysis** — RunMat parsed the file fine but its checker refuses
    it. The big one is definite-assignment (`RM-MIR0002`, "local may be read
    before assignment on some control-flow paths"). MATLAB has no such rule:
    reading a maybe-unassigned local is a runtime error only if that path is
    actually taken. Code rejected here often runs correctly:

        function y = g(x)
        if x > 0
            y = 1;
        end
        y = y + 0;
        end

    `runmat check` rejects it; `runmat run` prints 1 for g(5).

So the honest headline is not "N files pass check" but "N parse, of which M are
then refused by a checker rule MATLAB does not have".

Usage:
    tools/classify_sweep.py reports/parse_sweep_shimmed.json
"""

import json
import re
import sys

STATIC_ANALYSIS = re.compile(
    r"may be read before|not definitely assigned|definite assignment",
    re.I,
)
SYNTAX = re.compile(r"ParseError|expected|unexpected token", re.I)

TIER_ORDER = ["syntax", "static_analysis", "lowering", "runtime_semantics", "other"]

TIER_LABEL = {
    "syntax": "Syntax — RunMat cannot read the file",
    "static_analysis": "Static analysis — parsed fine, refused by a rule MATLAB lacks",
    "lowering": "Lowering/MIR — parsed, failed to compile",
    "runtime_semantics": "Semantics — undefined names, shape and type mismatches",
    "other": "Unclassified",
}


def tier_of(entry: dict) -> str:
    bucket = entry.get("bucket", "") or ""
    msg = entry.get("message", "") or ""
    if STATIC_ANALYSIS.search(msg):
        return "static_analysis"
    if "ParseError" in bucket or SYNTAX.search(msg):
        return "syntax"
    if "Mir" in bucket:
        return "lowering"
    if "UndefinedVariable" in bucket or "ShapeMismatch" in bucket:
        return "runtime_semantics"
    return "other"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    with open(path) as fh:
        data = json.load(fh)

    tiers = {t: [] for t in TIER_ORDER}
    for entry in data["results"]:
        if entry.get("ok"):
            continue
        tiers[tier_of(entry)].append(entry)

    total = data["total"]
    clean = data["parsed_ok"]
    syntax_bad = len(tiers["syntax"])
    parses = total - syntax_bad

    print(f"# Tiered parse sweep — {path}\n")
    print(f"- Files: **{total}**")
    print(f"- Fully clean under `runmat check`: **{clean}** "
          f"({100.0 * clean / total:.1f}%)")
    print(f"- Parse without a syntax error: **{parses}** "
          f"({100.0 * parses / total:.1f}%)")
    print(f"- Of the {total - clean} failures:\n")
    for t in TIER_ORDER:
        n = len(tiers[t])
        if n:
            print(f"  - **{n}** — {TIER_LABEL[t]}")
    print()

    # Rough payoff estimate. Each file records only its *first* error, so a file
    # counted against one blocker may well have others behind it. These are
    # therefore upper bounds on what fixing a single thing would unlock, useful
    # for ordering work rather than for promising an outcome.
    print("\n## Upper bound on what each blocker is worth\n")
    print("Each file reports only its first error, so a file counted here may")
    print("have further problems behind it. Read these as an ordering, not a")
    print("promise.\n")
    print("| First blocker | Files | Clean rate if fully fixed |")
    print("| --- | ---: | ---: |")
    groups = {
        "definite assignment (includes `global`)": STATIC_ANALYSIS,
        "undefined name (often a missing builtin)": re.compile(r"undefined variable", re.I),
        "brace indexing on a non-cell": re.compile(r"brace indexing requires", re.I),
        "syntax": SYNTAX,
    }
    counted = set()
    rows_out = []
    for label, pattern in groups.items():
        n = 0
        for i, entry in enumerate(data["results"]):
            if entry.get("ok") or i in counted:
                continue
            if pattern.search(entry.get("message") or ""):
                counted.add(i)
                n += 1
        if n:
            rows_out.append((label, n))
    for label, n in sorted(rows_out, key=lambda r: -r[1]):
        print(f"| {label} | {n} | {100.0 * (clean + n) / total:.0f}% |")

    for t in TIER_ORDER:
        rows = tiers[t]
        if not rows:
            continue
        print(f"\n## {TIER_LABEL[t]} ({len(rows)})\n")
        sigs = {}
        for r in rows:
            key = (r.get("message") or "")[:90]
            sigs.setdefault(key, []).append(r["file"])
        for key, files in sorted(sigs.items(), key=lambda kv: -len(kv[1]))[:12]:
            print(f"- {len(files)} x — {key or '(no message)'}")
            for f in files[:3]:
                print(f"    - `{f}`")
    return 0


if __name__ == "__main__":
    sys.exit(main())
