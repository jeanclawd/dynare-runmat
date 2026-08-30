# dynare-runmat

Compatibility work toward running [Dynare](https://www.dynare.org) — the MATLAB
toolbox for solving and estimating DSGE macroeconomic models — on
[RunMat](https://runmat.com), an open-source Rust runtime for MATLAB/Octave
syntax.

This repository is **not** a fork of Dynare. It is a measurement rig: a set of
harnesses that run Dynare's real source against RunMat, classify what breaks,
and track the gap as it closes.

## Why this is hard

Dynare is ~1,000 `.m` files of mature, idiomatic MATLAB. It leans on the parts
of the language that are easy to write and hard to reimplement: struct
auto-vivification, `switch` on strings, sparse linear algebra, and — at the core
of its first-order perturbation solver — the generalized Schur (QZ)
decomposition with eigenvalue reordering.

So "does it run" is the wrong first question. The useful questions are *how far
does it get*, and *which specific gap is in the way*.

Measuring turned up an answer that was not the expected one. The biggest
obstacle is not a missing feature at all: it is that `runmat check` enforces a
static type discipline MATLAB does not have, and rejects a great deal of
ordinary Dynare code that executes perfectly well when run. Separating "RunMat
cannot read this" from "RunMat read it and refused it" is therefore the first
job of any honest measurement here, and it is why this repo reports two numbers
rather than one.

## What's here

| Path | What it does |
| --- | --- |
| `tools/parse_sweep.py` | Runs `runmat check` over every `.m` file in a tree; classifies failures by error id and message signature. |
| `tools/mfile_shim.py` | Rewrites MATLAB files into a form RunMat can parse (adds terminating `end`s), so the *next* tier of failures becomes visible. |
| `tools/conformance.py` | Semantic suite runner: does RunMat *behave* like MATLAB on the features Dynare depends on? |
| `tools/runtime_probe.py` | Takes real functions out of the Dynare tree, calls them with real inputs, and checks the answer against MATLAB's. |
| `tools/check_conformance.py` | Valid MATLAB that `runmat check` rejects, and whether it nonetheless runs — which separates a checker bug from a runtime gap. |
| `tools/classify_sweep.py` | Splits sweep failures into syntax vs checker rejections, and estimates what each blocker is worth. |
| `tools/subsystem_report.py` | Groups a sweep by Dynare subsystem, to show which parts are closest to running. |
| `tools/gen_suite.py` | Authors the conformance cases as real `.m` / `.expected` files. |
| `tests/conformance/` | The runtime suite — readable, runnable, editable by hand. |
| `tests/check/` | The check-level suite: legal MATLAB the checker refuses. |
| `reports/` | Generated results (JSON + Markdown). |

## Results

Measured against **RunMat 0.6.2** and **Dynare 8-unstable** (`0fad4db`).
See `reports/` for the full breakdown and `FINDINGS.md` for the prioritized list.

### Parse sweep — can RunMat read Dynare at all?

| Tree | Files | Parses (no syntax error) | Fully clean under `runmat check` |
| --- | --- | --- | --- |
| Dynare `matlab/` as-is | 1056 | 221 (20.9%) | 63 (**5.97%**) |
| After `mfile_shim.py` | 1056 | 998 (**94.5%**) | 294 (27.8%) |

Two columns, because `runmat check` conflates two very different things.

The as-is rate is dominated by a single cause: RunMat requires every `function`
to be closed by a terminating `end`, and classic MATLAB function files omit it.
824 of Dynare's 1056 files are written that way. That one rule masks every other
incompatibility, which is why the shim exists — and with it gone, **94.5% of
Dynare parses**. Only 58 files have a genuine syntax problem left.

The gap between 94.5% and 27.8% is almost entirely RunMat's checker enforcing
rules MATLAB does not have — chiefly definite assignment, which does not
understand `global` and so rejects every file that reads `M_`, `oo_`, or
`options_`. Code it refuses frequently runs correctly.
`tools/classify_sweep.py` splits the tiers; see
`reports/parse_sweep_shimmed_tiered.md`.

### What the checker rejects that MATLAB accepts

The single largest cause of sweep failures is not RunMat failing to read
Dynare — it is `runmat check` enforcing a static discipline the language does
not have. `tests/check/` pins each case and then tries to run it, which is what
separates a checker bug from a real runtime gap:

| Case | Rejected with | Runs anyway? |
| --- | --- | --- |
| local assigned in one branch, read after | `RM-MIR0002` | ✅ returns 1 |
| `global M_` then reading `M_.foo` | `RM-MIR0001` | ✅ returns 42 |
| brace-indexing a parameter, `c{i}` | `RM-TYPE-BRACE-INDEX` | ✅ returns 20 |
| `feval(fs{i}, ...)` | `RunMat:HirError` | ❌ fails at run time too |
| param reassigned in a nested `if`, then indexed | **stack overflow, process aborts** | ❌ crashes `run` too |

A separate hazard worth knowing before trusting any measurement here:
`runmat run` analyses every `.m` file beside the script and aborts on a static
error in any of them, naming no file. Both harnesses therefore copy each case
into its own temp directory before running it. `runmat check` is unaffected, so
the parse-sweep numbers above were never at risk.

The first three are checker-only and account for roughly 450 of the 762
shimmed-tree failures. The stack overflow is the most severe single item found:
an 8-line function aborts the process outright, in both `check` and `run`, and
34 Dynare files hit it — they are exactly the sweep entries that carry no error
message, because the process dies before printing one. The fourth is a genuine limitation: a brace index is
treated as a comma-list expansion even with a scalar index, so a function
selected out of a cell cannot be `feval`'d — which is how Dynare dispatches
per-block model functions.

### Running real Dynare functions

14 functions lifted out of the shimmed tree and called with real inputs: **11
return MATLAB's exact answer**. All three failures share one cause — `NaN(n,m)`
is not callable, though `nan(n,m)` is.

### Semantic conformance

117 hand-written cases across structs, cells, functions, strings, constructors,
complex arithmetic, printf formats, platform builtins, concatenation, dense and sparse linear
algebra, error handling, indexing, control flow, file I/O, RNG reproducibility,
and multi-file structure. Each case pins the exact output MATLAB produces; numeric
cases assert a mathematical identity rather than a text format.

**83 pass, 34 are tracked known gaps, 0 unexpected failures.**

Most cases are one file. Features that cannot be — `classdef`, `+package`
namespaces, cross-file resolution — are directories holding a `main.m` plus
support files, copied to a temp dir and run there — which also keeps cases
that write files from littering the repo. All five structural cases pass,
including `classdef` inside an `@dir`, exactly how Dynare's `@dprior` is
written.

Known gaps are marked `xfail` **with a reason**, so the suite stays green
against today's RunMat and any *new* breakage — or any *fix* (reported as
`xpass`) — shows up immediately.

## Running it

RunMat 0.6.2's prebuilt Linux binary links against HDF5 1.10
(`libhdf5_serial.so.103`), which recent distros no longer ship. See
`docs/environment.md` for the workaround used here.

```bash
# 1. Get Dynare (canonical remote; the old GitHub mirror is gone)
git clone --depth 1 https://git.dynare.org/Dynare/dynare.git ../dynare-upstream

# 2. Baseline: what parses as-is?
python3 tools/parse_sweep.py --root ../dynare-upstream/matlab \
                             --out reports/parse_sweep_raw

# 3. Remove the terminating-`end` wall, then re-sweep
python3 tools/mfile_shim.py --in-root ../dynare-upstream/matlab \
                            --out-root build/shimmed
python3 tools/parse_sweep.py --root build/shimmed \
                             --out reports/parse_sweep_shimmed

# 4. Semantic conformance
python3 tools/gen_suite.py tests/conformance
python3 tools/conformance.py --suite tests/conformance --out reports/conformance

# 5. Run actual Dynare functions
python3 tools/runtime_probe.py --tree build/shimmed --out reports/runtime_probe
```

## Status

The parse wall is characterized and removable — 94.5% of Dynare parses once the
terminating-`end` rule is out of the way. Real Dynare functions run and return
correct answers. The semantic gaps are enumerated, reproduced individually, and
tracked as tests.

Nothing here solves a model yet, and the reason is specific: the QZ family
(`qz`, `ordqz`, `schur`) does not exist in RunMat. Without a generalized Schur
decomposition with eigenvalue reordering there is no Blanchard-Kahn split and
therefore no first-order policy function. Everything else on the list is a
compatibility patch; that one is numerical work.

See `FINDINGS.md` for the prioritized list, each item with a standalone repro.

## License

Tooling here is MIT. Dynare itself is GPL-3.0-or-later and is not vendored into
this repository.
