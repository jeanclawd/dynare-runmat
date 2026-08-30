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
auto-vivification, comma-separated lists, `switch` on strings, sparse linear
algebra, and — at the core of its first-order perturbation solver — the
generalized Schur (QZ) decomposition with eigenvalue reordering.

So "does it run" is the wrong first question. The useful questions are *how far
does it get*, and *which specific gap is in the way*.

## What's here

| Path | What it does |
| --- | --- |
| `tools/parse_sweep.py` | Runs `runmat check` over every `.m` file in a tree; classifies failures by error id and message signature. |
| `tools/mfile_shim.py` | Rewrites MATLAB files into a form RunMat can parse (adds terminating `end`s), so the *next* tier of failures becomes visible. |
| `tools/conformance.py` | Semantic suite runner: does RunMat *behave* like MATLAB on the features Dynare depends on? |
| `tools/runtime_probe.py` | Takes real functions out of the Dynare tree, calls them with real inputs, and checks the answer against MATLAB's. |
| `tools/gen_suite.py` | Authors the conformance cases as real `.m` / `.expected` files. |
| `tests/conformance/` | The suite itself — readable, runnable, editable by hand. |
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

### Running real Dynare functions

14 functions lifted out of the shimmed tree and called with real inputs: **11
return MATLAB's exact answer**. All three failures share one cause — `NaN(n,m)`
is not callable, though `nan(n,m)` is.

### Semantic conformance

79 hand-written cases across structs, cells, functions, strings, constructors,
dense and sparse linear algebra, error handling, indexing, and control flow.
Each case pins the exact output MATLAB produces; numeric cases assert a
mathematical identity rather than a text format.

**57 pass, 22 are tracked known gaps, 0 unexpected failures.**

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
