#!/usr/bin/env python3
"""Self-tests for mfile_shim.

The shim rewrites source, so a bug in it silently corrupts every downstream
measurement. Two properties guard it:

  * **Idempotency.** Shimming an already-shimmed file must be a no-op. When it
    is not, the shim under-closed the file — which is exactly how the
    quote-vs-transpose bug was found: `[name1 ' text']` read the quote as a
    transpose, the unterminated string swallowed the closing bracket, bracket
    depth never came back to zero, and every later `end` was ignored as an
    index.

  * **Unit cases.** Specific constructs that are easy to get wrong.

Usage:
    tools/test_shim.py                       # unit cases only
    tools/test_shim.py --tree ../dynare-upstream/matlab --sample 250
"""

import argparse
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mfile_shim import shim_text, strip_code  # noqa: E402

CASES = [
    # (name, source, expected number of `end`s added)
    ("unterminated single function",
     "function y = f(x)\ny = x + 1;\n", 1),
    ("already terminated",
     "function y = f(x)\ny = x + 1;\nend\n", 0),
    ("two unterminated functions",
     "function y = f(x)\ny = g(x);\nfunction y = g(x)\ny = 1;\n", 2),
    ("script with no function",
     "x = 1;\ndisp(x);\n", 0),
    ("end as an index is not a block end",
     "function y = f(v)\ny = v(end);\n", 1),
    ("end inside a range",
     "function y = f(v)\ny = v(2:end-1);\n", 1),
    ("if block already closed",
     "function y = f(x)\nif x > 0\ny = 1;\nelse\ny = 2;\nend\n", 1),
    ("string containing the word end",
     "function f()\ndisp('end');\n", 1),
    ("comment containing the word end",
     "function f()\n% end of story\ndisp(1);\n", 1),
    ("bracketed string after identifier",
     "function f(name1)\ndisp([name1 ' is bad']);\nif 1\ndisp(2);\nend\n", 1),
    ("transpose is not a string",
     "function y = f(A)\ny = A';\nif 1\ny = 2;\nend\n", 1),
    ("nested for and if",
     "function y = f(n)\ny = 0;\nfor i = 1:n\nif mod(i, 2)\ny = y + i;\nend\nend\n", 1),
    ("switch block",
     "function y = f(x)\nswitch x\ncase 1\ny = 1;\notherwise\ny = 2;\nend\n", 1),
    ("try catch",
     "function f()\ntry\nerror('x');\ncatch\ndisp('c');\nend\n", 1),
]


def run_unit_cases() -> int:
    failures = 0
    for name, src, want in CASES:
        _new, _changed, added = shim_text(src)
        ok = added == want
        print(f"  {'ok  ' if ok else 'FAIL'}  {name}: added {added}, want {want}")
        failures += 0 if ok else 1
    return failures


def check_strip_code() -> int:
    failures = 0
    checks = [
        ("a = 1; % end", "a = 1; "),
        ("disp('end')", "disp('')"),
        ("y = A';", "y = A';"),
        ("disp([n ' x'])", "disp([n ''])"),
    ]
    for src, want in checks:
        got, _ = strip_code(src, False)
        ok = got == want
        print(f"  {'ok  ' if ok else 'FAIL'}  strip_code({src!r}) -> {got!r}"
              f"{'' if ok else f' want {want!r}'}")
        failures += 0 if ok else 1
    return failures


def check_idempotency(tree: str, sample_size: int) -> int:
    files = []
    for dirpath, _d, filenames in os.walk(tree):
        for fn in filenames:
            if fn.endswith(".m"):
                files.append(os.path.join(dirpath, fn))
    if not files:
        print(f"  no .m files under {tree}")
        return 1
    random.seed(0)
    sample = random.sample(files, min(sample_size, len(files)))

    bad = []
    for path in sample:
        with open(path, "r", errors="replace") as fh:
            text = fh.read()
        once, _c, _a = shim_text(text)
        _twice, changed, added = shim_text(once)
        if changed:
            bad.append((path, added))

    print(f"  re-shimmed {len(sample)} files; {len(bad)} were not idempotent")
    for path, added in bad[:10]:
        print(f"    would add {added} more `end`s: {path}")
    return len(bad)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tree", help="Dynare matlab tree for the idempotency check")
    ap.add_argument("--sample", type=int, default=250)
    args = ap.parse_args()

    print("strip_code:")
    failures = check_strip_code()
    print("unit cases:")
    failures += run_unit_cases()

    if args.tree:
        print("idempotency over real source:")
        failures += check_idempotency(os.path.abspath(args.tree), args.sample)

    print(f"\n{'PASS' if failures == 0 else f'FAIL ({failures})'}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
