#!/usr/bin/env python3
"""Rewrite MATLAB .m files into a form RunMat 0.6.2 can parse.

The dominant blocker is that RunMat requires every `function` to be closed by a
terminating `end`, while classic MATLAB function files omit it. This module adds
the missing `end`s without touching anything else, so the *next* tier of
incompatibilities becomes visible.

The tricky part is deciding which `end` tokens are block terminators. Two things
masquerade as one:

  * `end` used as an index — `x(end)`, `v(2:end-1)`. These sit at paren depth > 0.
  * `end` inside a string or comment — `'end'`, `% end of loop`.

So the scanner strips strings/comments first (handling MATLAB's `'`
transpose-vs-quote ambiguity), then only counts keywords at bracket depth 0.

Usage:
    tools/mfile_shim.py --in-root ../dynare-upstream/matlab --out-root build/shimmed
    tools/mfile_shim.py --file foo.m --stdout
"""

import argparse
import os
import re
import sys

OPENERS = {
    "if", "for", "parfor", "while", "switch", "try", "function", "classdef",
    "properties", "methods", "events", "enumeration", "spmd", "arguments",
    "unwind_protect", "do",
}
# Octave/MATLAB block terminators. All of these close exactly one block.
CLOSERS = {
    "end", "endif", "endfor", "endwhile", "endfunction", "endswitch",
    "endparfor", "endproperties", "endmethods", "endevents", "endclassdef",
    "end_try_catch", "end_unwind_protect", "until",
}
# Keywords that continue a block rather than opening or closing one.
NEUTRAL = {"else", "elseif", "catch", "case", "otherwise"}

WORD = re.compile(r"[A-Za-z_]\w*")
# A `'` is a transpose operator (not a string start) when it directly follows
# one of these — an identifier, a number, or a closing bracket.
TRANSPOSE_AFTER = re.compile(r"[\w\)\]\}\.']$")


def strip_code(line: str, in_block_comment: bool):
    """Return (code_only_line, still_in_block_comment).

    Strings become empty quotes and comments are removed, so keyword scanning
    never trips over `% end` or `'end'`.
    """
    stripped = line.strip()

    if in_block_comment:
        # %} on its own line closes a block comment.
        if re.match(r"^%\}\s*$", stripped) or re.match(r"^#\}\s*$", stripped):
            return "", False
        return "", True

    if re.match(r"^%\{\s*$", stripped) or re.match(r"^#\{\s*$", stripped):
        return "", True

    out = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]

        if ch in "%#":
            break  # rest of line is a comment

        if ch == '"':
            i += 1
            while i < n:
                if line[i] == '"':
                    if i + 1 < n and line[i + 1] == '"':
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            out.append('""')
            continue

        if ch == "'":
            prev = "".join(out).rstrip()
            if prev and TRANSPOSE_AFTER.search(prev):
                out.append("'")  # transpose operator
                i += 1
                continue
            i += 1
            while i < n:
                if line[i] == "'":
                    if i + 1 < n and line[i + 1] == "'":
                        i += 2
                        continue
                    i += 1
                    break
                i += 1
            out.append("''")
            continue

        out.append(ch)
        i += 1

    return "".join(out), False


def scan_tokens(code: str, depth_in: int):
    """Yield (keyword, bracket_depth) for words in `code`, tracking brackets.

    `depth_in` carries bracket depth across continuation lines.
    """
    depth = depth_in
    i = 0
    n = len(code)
    toks = []
    while i < n:
        ch = code[i]
        if ch in "([{":
            depth += 1
            i += 1
            continue
        if ch in ")]}":
            depth = max(0, depth - 1)
            i += 1
            continue
        m = WORD.match(code, i)
        if m:
            toks.append((m.group(0), depth))
            i = m.end()
            continue
        i += 1
    return toks, depth


def analyze(lines):
    """Return (needs_end_style, function_line_indexes, final_block_depth).

    `needs_end_style` is True when the file uses classic unterminated functions.
    """
    in_block_comment = False
    bracket_depth = 0
    block_depth = 0
    func_lines = []
    # Depth recorded at each `function` keyword, before it opens its own block.
    func_depths = []
    continuation = False

    for idx, raw in enumerate(lines):
        code, in_block_comment = strip_code(raw, in_block_comment)
        if not code.strip():
            continue

        toks, bracket_depth = scan_tokens(code, bracket_depth)

        # Only the first keyword of a statement can open/close a block, except
        # for one-line constructs like `if x, y=1; end` — so scan all tokens at
        # bracket depth 0 and let the depth arithmetic sort it out.
        for word, bdepth in toks:
            if bdepth != 0:
                continue  # `end` as an index, or a name inside a call
            if word == "function" and not continuation:
                func_lines.append(idx)
                func_depths.append(block_depth)
                block_depth += 1
            elif word in OPENERS:
                block_depth += 1
            elif word in CLOSERS:
                block_depth = max(0, block_depth - 1)
            elif word in NEUTRAL:
                pass

        continuation = code.rstrip().endswith("...")

    return func_lines, func_depths, block_depth


def shim_text(text: str):
    """Return (new_text, changed, n_added)."""
    lines = text.splitlines()
    if not lines:
        return text, False, 0

    func_lines, func_depths, block_depth = analyze(lines)
    if not func_lines:
        return text, False, 0  # plain script, nothing to close

    # If every function was closed the depth returns to 0 and each subsequent
    # `function` starts at depth 0 too. Unterminated style shows up as a
    # positive leftover depth equal to the number of open functions.
    if block_depth <= 0:
        return text, False, 0

    # Insert an `end` immediately before every `function` line after the first,
    # and one at EOF. Only do this for functions that were left open (depth
    # grew monotonically), which is the classic style.
    out = []
    added = 0
    for idx, line in enumerate(lines):
        if idx in func_lines and func_lines.index(idx) > 0:
            out.append("end")
            added += 1
        out.append(line)

    # Close the final function (and any still-open ones).
    remaining = block_depth - added
    for _ in range(max(0, remaining)):
        out.append("end")
        added += 1

    return "\n".join(out) + "\n", True, added


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in-root")
    ap.add_argument("--out-root")
    ap.add_argument("--file")
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args()

    if args.file:
        with open(args.file, "r", errors="replace") as fh:
            text = fh.read()
        new, changed, added = shim_text(text)
        if args.stdout:
            sys.stdout.write(new)
        else:
            print(f"{args.file}: changed={changed} added={added}", file=sys.stderr)
        return 0

    if not (args.in_root and args.out_root):
        ap.error("need --in-root and --out-root (or --file)")

    in_root = os.path.abspath(args.in_root)
    out_root = os.path.abspath(args.out_root)
    n_files = n_changed = n_added = 0

    for dirpath, _dirnames, filenames in os.walk(in_root):
        for fn in filenames:
            src = os.path.join(dirpath, fn)
            rel = os.path.relpath(src, in_root)
            dst = os.path.join(out_root, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if not fn.endswith(".m"):
                continue
            with open(src, "r", errors="replace") as fh:
                text = fh.read()
            new, changed, added = shim_text(text)
            with open(dst, "w") as fh:
                fh.write(new)
            n_files += 1
            n_changed += int(changed)
            n_added += added

    print(f"shimmed {n_files} files; {n_changed} rewritten; {n_added} `end`s added")
    return 0


if __name__ == "__main__":
    sys.exit(main())
