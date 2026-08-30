#!/usr/bin/env python3
"""Execute real Dynare functions under RunMat and check their answers.

Parsing is necessary but not sufficient. This harness takes actual functions
out of the Dynare tree (after `mfile_shim.py`), calls them with real inputs,
and compares against the value MATLAB returns.

Each probe runs in its own directory with the function file(s) copied in, so
RunMat resolves them from the working directory and one probe cannot affect
another.

Usage:
    tools/runtime_probe.py --tree build/shimmed --out reports/runtime_probe
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

NOISE = re.compile(r"wgpu|libEGL|DRI2|No config found|No windowing system|WARN")

# (probe name, [dynare function files needed], driver code, expected stdout)
PROBES = [
    ("dynsec2hms", ["dynsec2hms.m"],
     "fprintf('%s\\n', dynsec2hms(3725));",
     "1h02m05s"),

    ("dynsec2hms_zero", ["dynsec2hms.m"],
     "fprintf('%s\\n', dynsec2hms(0));",
     "0h00m00s"),

    ("dyn_vech", ["dyn_vech.m"],
     "v = dyn_vech([1 2; 2 3]);\nfprintf('%d\\n', v);",
     "1\n2\n3"),

    ("dyn_unvech", ["dyn_unvech.m"],
     "M = dyn_unvech([1; 2; 3]);\nfprintf('%d %d %d %d\\n', "
     "M(1,1), M(1,2), M(2,1), M(2,2));",
     "1 2 2 3"),

    ("vech_roundtrip", ["dyn_vech.m", "dyn_unvech.m"],
     "A = [4 1; 1 9];\nB = dyn_unvech(dyn_vech(A));\n"
     "fprintf('%d\\n', isequal(A, B));",
     "1"),

    ("cellofchararraymaxlength", ["cellofchararraymaxlength.m"],
     "fprintf('%d\\n', cellofchararraymaxlength({'ab', 'cdef', 'g'}));",
     "4"),

    ("exactstrrep", ["exactstrrep.m"],
     "fprintf('%s\\n', exactstrrep('a bc b', 'b', 'X'));",
     "a bc X"),

    ("dynare_squeeze_row", ["dynare_squeeze.m"],
     "B = dynare_squeeze([1 2 3]);\nfprintf('%d %d\\n', size(B,1), size(B,2));",
     "3 1"),

    ("dynare_squeeze_col", ["dynare_squeeze.m"],
     "B = dynare_squeeze([1; 2; 3]);\nfprintf('%d %d\\n', size(B,1), size(B,2));",
     "3 1"),

    ("skipline", ["skipline.m"],
     "skipline(2);\nfprintf('done\\n');",
     "\n\ndone"),
]


def clean(text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if not NOISE.search(ln)]
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", required=True, help="shimmed Dynare matlab tree")
    ap.add_argument("--out", required=True)
    ap.add_argument("--runmat", default="runmat")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    tree = os.path.abspath(args.tree)
    results = []
    started = time.time()

    for name, needs, driver, expected in PROBES:
        missing = [f for f in needs if not os.path.exists(os.path.join(tree, f))]
        if missing:
            results.append({"probe": name, "status": "missing_source",
                            "missing": missing})
            continue

        with tempfile.TemporaryDirectory() as td:
            for f in needs:
                shutil.copy(os.path.join(tree, f), os.path.join(td, f))
            drv = os.path.join(td, "driver.m")
            with open(drv, "w") as fh:
                fh.write(driver.rstrip() + "\n")
            try:
                proc = subprocess.run(
                    [args.runmat, "run", "driver.m"],
                    cwd=td, capture_output=True, text=True, timeout=args.timeout,
                )
                out, err, rc = proc.stdout, proc.stderr, proc.returncode
            except subprocess.TimeoutExpired:
                out, err, rc = "", "TIMEOUT", -9

        actual = clean(out)
        exp = clean(expected)
        status = "pass" if actual == exp else "fail"
        entry = {"probe": name, "status": status, "functions": needs,
                 "expected": exp, "actual": actual, "returncode": rc}
        if status == "fail":
            entry["stderr"] = clean(err)[:500]
        results.append(entry)

    n = len(results)
    n_pass = sum(1 for r in results if r["status"] == "pass")
    payload = {
        "tree": tree,
        "total": n,
        "passed": n_pass,
        "pass_rate": round(100.0 * n_pass / n, 2) if n else 0.0,
        "results": results,
        "elapsed_sec": round(time.time() - started, 1),
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out + ".json", "w") as fh:
        json.dump(payload, fh, indent=2)

    with open(args.out + ".md", "w") as fh:
        fh.write("# Running real Dynare functions under RunMat\n\n")
        fh.write("Functions taken from the shimmed Dynare tree, called with real "
                 "inputs, compared against MATLAB's answer.\n\n")
        fh.write(f"- Probes: **{n}**\n- Passing: **{n_pass}** "
                 f"({payload['pass_rate']}%)\n\n")
        for r in results:
            mark = {"pass": "✅", "fail": "❌"}.get(r["status"], "❔")
            fh.write(f"### {mark} `{r['probe']}`\n\n")
            fh.write(f"- source: {', '.join(r.get('functions', []))}\n")
            if r["status"] == "fail":
                fh.write(f"- expected: `{r['expected']!r}`\n")
                fh.write(f"- actual: `{r['actual']!r}`\n")
                if r.get("stderr"):
                    fh.write(f"- error:\n\n```\n{r['stderr']}\n```\n")
            fh.write("\n")

    print(json.dumps({k: payload[k] for k in
                      ("total", "passed", "pass_rate", "elapsed_sec")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
