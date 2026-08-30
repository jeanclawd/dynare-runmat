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

| Tree | Files | Parsed clean | Rate |
| --- | --- | --- | --- |
| Dynare `matlab/` as-is | 1056 | 63 | **5.97%** |
| After `mfile_shim.py` | 1056 | see `reports/parse_sweep_shimmed.md` | |

The as-is number is dominated by a single cause: RunMat requires every
`function` to be closed by a terminating `end`, and classic MATLAB function
files omit it. 844 of Dynare's 1056 files are written that way. That one rule
masks every other incompatibility, which is why the shim exists.

### Semantic conformance

74 hand-written cases across structs, cells, functions, strings, dense and
sparse linear algebra, error handling, indexing, and control flow. Each case
pins the exact output MATLAB produces; numeric cases assert a mathematical
identity rather than a text format.

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

Early. The parse wall is characterized and removable; the semantic gaps are
enumerated and tracked. The blocking item for actually *solving a model* is the
missing QZ/`ordqz` family — without generalized Schur with eigenvalue
reordering there is no Blanchard-Kahn split and no first-order policy function.

## License

Tooling here is MIT. Dynare itself is GPL-3.0-or-later and is not vendored into
this repository.
