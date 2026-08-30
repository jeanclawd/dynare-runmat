# Findings: RunMat 0.6.2 vs Dynare 8-unstable

Every item below was reproduced against RunMat 0.6.2 on Linux x86_64 with a
minimal standalone snippet, not inferred from a sweep statistic. The snippet is
included so each one can be checked in seconds.

Ordered by what blocks Dynare soonest.

---

## P0 — blocks parsing the toolbox at all

### 1. Functions without a terminating `end` fail to parse

Classic MATLAB function files do not close their functions. RunMat requires it.

```matlab
% addone.m
function y = addone(x)
y = x + 1;
```

```
error: Could not parse function source 'addone.m':
       Syntax error at position 0: expected 'end'
id: RunMat:FunctionParseError
```

Adding `end` makes it work. **844 of Dynare's 1056 `.m` files are written in the
unterminated style**, and this single rule is responsible for the bulk of the
5.97% as-is parse rate. It also masks every other incompatibility in those
files, which is why `tools/mfile_shim.py` exists.

MATLAB's actual rule: within one file, functions must *consistently* either all
terminate with `end` or all omit it. Both forms are legal.

---

## P0 — measurement caveat: `runmat check` is stricter than `runmat run`

RunMat's checker enforces **definite assignment**, a rule MATLAB does not have.

```matlab
function y = g(x)
if x > 0
    y = 1;
end
y = y + 0;
end
```

```
error[RM-MIR0002]: local may be read before assignment on some control-flow paths
 --> cf2.m:5:1
  = help: assign this local on every control-flow path before reading it
```

But `g(5)` runs and returns `1`. In MATLAB, reading a maybe-unassigned local is
an error only if that path is actually taken; RunMat rejects the function ahead
of time. This pattern — assign in one branch, read after — is ordinary MATLAB
and common in Dynare.

### The same analysis does not understand `global`

Worse, and more specific:

```matlab
function y = f()
global M_
y = M_.foo;
end
```

```
error[RM-MIR0001]: local may be read before it is assigned
 --> uv2.m:3:1
  = help: assign this local before reading it
```

The `global M_` declaration is not treated as bringing `M_` into scope, so
every read of a global looks like a read of an unassigned local. At runtime
globals work correctly — this exact pattern prints `42`:

```matlab
global M_
M_ = struct('foo', 42);
fprintf('%d\n', readit());
function y = readit()
global M_
y = M_.foo;
end
```

**123 Dynare files declare globals**, and `M_`, `oo_`, and `options_` are the
toolbox's central data structures. This one checker rule accounts for the
largest single failure bucket in the sweep.

By contrast, calling a function RunMat cannot locate is only a *warning*
(`RM-RES0001`), which is the right severity — that one is fine.

### And it rejects brace indexing of a parameter

A third instance of the same pattern, and the next-largest bucket after the two
above — **88 files**:

```matlab
function y = pick(c, i)
y = c{i};
end
```

```
error[RM-TYPE-BRACE-INDEX]: brace indexing requires a cell-like value
 --> bi.m:2:1
  = static value contract is not satisfied here
```

`pick({10, 20}, 2)` runs and returns `20`. RunMat cannot prove a parameter is a
cell, so it refuses `{}` on it ahead of time. Passing a cell array into a
function and indexing it is entirely ordinary MATLAB — in Dynare it is how
`var_list`, `endo_names` and every other name list is handled.

Taken together, definite assignment, `global`, and this parameter contract are
one story: **`runmat check` enforces a static type discipline the language does
not have.** They are the three largest failure buckets in the sweep, and in
every case the code runs correctly.

The long tail says the same thing in smaller numbers — each of these is a
static proof failing on code whose types are only known at runtime:

```
index for dimension 2 is outside the proven bound 0
operator is not defined for the proven operand value category
right-division column dimensions 1 and 2 do not agree
transpose requires a numeric, logical, or character value
```

A genuine limitation rather than over-strictness, also in that tail (7 files):

```matlab
function y = call(fs, i, a, b)
y = feval(fs{i}, a, b);
end
```

```
error: feval: function argument cannot be a comma-list expansion
id: RunMat:HirError
```

A brace index is treated as a comma-list expansion even when the index is a
scalar, so a function selected out of a cell array cannot be `feval`'d. This is
how Dynare dispatches per-block model functions
(`feval(funcs{blk}, ...)`). Note that `feval(f, args{:})` — expansion in the
*argument* position — works fine; it is specifically the function position.

Unlike the checker gaps above, this one fails at run time too.

Two consequences:

1. It is a real compatibility gap. A tool that refuses to load valid MATLAB is
   a blocker even when the runtime would have coped.
2. It distorts any sweep built on `runmat check`. **355 of the shimmed tree's
   failures are this rule**, not syntax. `tools/classify_sweep.py` separates
   the tiers so the headline number does not overstate the damage.

---

## P1 — a stray `.m` file in the directory breaks unrelated scripts

`runmat run` eagerly analyses every `.m` file sitting beside the script. A
static error in any one of them aborts the run — and the message names no file,
so it looks like a fault in the script you asked for.

```
/tmp/demo/good.m           M = [1 2; 3 4]; disp(size(M));
/tmp/demo/unrelated.m      function M = f(a)
                           M = [a; 1 2];
                           end
```

```
$ runmat run good.m
error: tensor literal rows must have consistent column counts
id: RunMat:AggregateShapeMismatch
```

`good.m` never calls `unrelated.m`. Delete the sibling and `good.m` prints
`2 2`. The behaviour is limited to the script's own directory — subdirectories
do not contaminate — and **`runmat check` is unaffected**; only `run` is.

This matters twice over for Dynare. Its `matlab/` directories hold dozens of
files each, so one file RunMat cannot analyse takes its whole directory down
with it. And it is a trap for anyone measuring compatibility: it cost me a
false finding here — "vertical concatenation is broken" — that evaporated the
moment I re-ran the same code in an empty directory. Both harnesses in this
repo now copy each case into a temp directory before running it, and the
regression is pinned as `tests/conformance/multifile/sibling_file_isolation`.

---

## P1 — blocks running ordinary Dynare code

### 2. `switch` on a string errors

```matlab
x = 'b';
switch x
case 'b'
    disp('B');
end
```

```
error: cannot convert CharArray(CharArray { data: ['b'], ... }) to f64
id: RunMat:RuntimeError
```

`switch` on a numeric value works. The operand is being coerced to `f64`
unconditionally. String dispatch is pervasive in Dynare — option parsing, solver
selection, model-type branching.

### 3. Struct auto-vivification is not supported

```matlab
s.a = 1;      % error: Undefined variable: s
```

MATLAB creates `s` as a struct on first field assignment. RunMat requires it to
exist:

```matlab
s = struct();
s.a.b = 3;    % this works
```

Dynare builds `M_`, `oo_`, and `options_` by assigning into fields of variables
that are frequently not pre-declared. Related: `s(1).a = 1; s(2).a = 2;`
(indexed auto-vivification into a struct array) also fails.

### 4. `eval` does not create variables in the caller's scope

```matlab
eval('w = 6;');
fprintf('%d\n', w);   % error: undefined variable 'w'
```

Dynare uses `eval` for dynamically-named model artifacts.

### 5. `str2func` does not evaluate an anonymous-function string

```matlab
h = str2func('@(x) x * 3');
h(4)    % error: Undefined function: (x) x * 3
```

The string is treated as a function *name* rather than parsed as a lambda.

---

## P1 — `NaN(...)` and `Inf(...)` are not callable, but `nan(...)` and `inf(...)` are

```matlab
nan(2, 3)     % works — 2x3 of NaN
NaN(2, 3)     % error: Undefined function: NaN
inf(2, 2)     % works
Inf(2, 2)     % error: Undefined function: Inf
disp(NaN)     % works — the bare constant is fine
```

In MATLAB the capitalized and lowercase spellings are the same function. In
RunMat the capitalized ones resolve as constants only, so calling them with
size arguments fails.

**188 Dynare files use the capitalized form.** It is the single cause of every
runtime-probe failure so far: `dyn_vech`, `dyn_unvech`, and their round-trip all
die on `Vector = NaN(n*(n+1)/2, 1)`.

This looks like the cheapest high-value fix on the list — a builtin-resolution
alias, not a semantic change.

---

## P2 — missing builtins Dynare depends on

### 6. A matrix row that is a bare variable is counted as one column

12 files. This one is not over-strictness — it fails at run time too.

```matlab
a = [3 4];
M = [a; 1 2];     % MATLAB: 2x2. RunMat: error
M = [1 2; a];     % same
```

```
error: tensor literal rows must have consistent column counts
id: RunMat:AggregateShapeMismatch
```

RunMat appears to count *elements* in each row rather than columns, so the row
`a` scores 1 against the row `1 2`'s 2. The neighbouring forms are all fine,
which is what makes it easy to miss:

| Form | Result |
| --- | --- |
| `[1 2; 3 4]` | works |
| `[a; b]` (both `1x2`) | works |
| `[A; a]` (`2x2` and `1x2`) | works |
| `[a b]` horizontal | works |
| `vertcat(a, b)` | works |
| `[a; 1 2]` | **fails** |
| `[1 2; a]` | **fails** |

So it is specifically a bare variable sharing a literal with a multi-element
row. `vertcat` is a working substitute.

### 7. Basic platform builtins are missing — `filesep` is in 118 Dynare files

```matlab
exist('filesep')   % 0
exist('ispc')      % 0
exist('isunix')    % 0
exist('ismac')     % 0
exist('computer')  % 0
```

Present and working: `pathsep`, `fullfile`, `fileparts`, `tempdir`, `getenv`.

Dynare usage: `filesep` **118 files**, `ispc` 21, `isunix` 7, `ismac` 7,
`computer` 5. `filesep` is the most-used missing builtin found so far and is a
one-line implementation. It is the top blocker for the `ms-sbvar` subsystem.

### 8. The QZ family is absent — this blocks model solution outright

```matlab
exist('qz')       % 0
exist('ordqz')    % 0
exist('schur')    % 0
```

This is the most consequential gap. Dynare's first-order perturbation solver
computes a **generalized Schur (QZ) decomposition** of the model's linearized
system, then **reorders the eigenvalues** to split stable from unstable roots —
that is the Blanchard-Kahn condition check and the source of the policy
function. Without `qz` and `ordqz` (or an equivalent), no DSGE model can be
solved, regardless of how much of the toolbox parses.

Also missing: `expm`, `sylvester`, `dlyap`, `orth`. `sylvester`-type solves
appear in second-order terms; `dlyap` in the unconditional variance of the
state.

Present and working: `eig`, `svd`, `chol`, `lu`, `kron`, `pinv`, `null`, `cond`,
`norm`, `rank`, `det`, `inv`, and dense `\`.

### 9. Sparse matrices exist but core operations reject them

```matlab
S = sparse(eye(3));
S * S      % error: mtimes: unsupported operand types
S \ [1;2]  % error: mldivide: unsupported input type SparseTensor
```

Construction, `full`, `nnz`, `issparse`, and `speye` all work — the type is
there, the operations are not. Dynare represents Jacobians sparsely throughout.

### 10. `ismember` rejects char and cellstr

```matlab
ismember('bb', {'aa', 'bb'})
% error: ismember: unsupported input type CharArray; expected numeric or logical
```

### 11. `strjoin` cannot consume a cell array of strings

```matlab
strjoin(strsplit('a,b,c', ','), '-')
% error: cannot convert to string array: Cell(CellArray { ... })
```

`strsplit` produces the cell array correctly; `strjoin` will not take it back.

---

## P3 — output and detail differences

### 12. `printf` numeric formats are wrong in several ways

| Format | Input | MATLAB | RunMat |
| --- | --- | --- | --- |
| `%e` | `1234.5` | `1.234500e+03` | `1.234500e3` |
| `%g` | `1` | `1` | `1.` |
| `%g` | `100000` | `100000` | `100000.` |
| `%g` | `0.00001` | `1e-05` | `1.00000e-5` |

Three distinct bugs: the exponent is missing its sign and two-digit padding,
`%g` leaves a trailing `.` on whole numbers, and `%g` keeps trailing zeros
instead of stripping them. `%f` and `%d` on integers are correct.

This is low severity per occurrence and high in aggregate — it silently changes
every Dynare log line, results table, and generated `.m` file that formats a
number this way.

Worth checking against a real MATLAB, which was not available here: `%d` given
a non-integer. RunMat prints `fprintf('%d', 2.5)` as `2`; MATLAB is documented
to switch to exponential notation for non-integer values given an integer
conversion. Flagged rather than asserted.

### 13. `exist` returns the wrong code for files

```matlab
exist('data.txt', 'file')   % MATLAB 2, RunMat 3
exist('some.m', 'file')     % MATLAB 2, RunMat 3
exist('sub', 'dir')         % 7 — correct
exist('q', 'var')           % 1 — correct
exist('nope.txt', 'file')   % 0 — correct
```

MATLAB's code 2 means "file"; 3 means "MEX or DLL". RunMat returns 3 for
ordinary files, so `exist(f) == 2` guards fail. Dynare has 5 such comparisons.
The directory, variable, and not-found codes are all right — only the file case
is off.

### 14. `regexp(..., 'tokens')` returns the wrong nesting

```matlab
t = regexp('x=12', '(\w+)=(\d+)', 'tokens');
t{1}{2}    % error: Cell index out of bounds
```

MATLAB returns a cell of matches, each itself a cell of that match's tokens.
RunMat's shape differs, so the standard `t{i}{j}` access fails.

---

## Structural features: all working

Worth stating plainly, because these were the most likely places for a
reimplementation to fall over, and none of them did:

| Feature | Status |
| --- | --- |
| `+package` namespaces (`mypkg.fn(x)`) | works |
| `import pkg.fn` | works |
| `classdef` with value semantics (copy on assign) | works |
| `classdef < handle` with reference semantics | works |
| `classdef` inside an `@dir` — Dynare's `@dprior` shape | works |
| Cross-file function resolution | works |
| Complex arithmetic, `abs`/`real`/`imag`/`conj`/`angle` | works |
| Complex eigenvalues, `sqrt` of a negative, complex matrix products | works |

Complex support mattering more than it looks: DSGE transition matrices have
complex eigenvalues in general, and the Blanchard-Kahn check counts how many
have modulus greater than one. `sum(abs(eig(A)) > 1)` gives the right answer.

File I/O and RNG also hold up, which matters for estimation:

| Feature | Status |
| --- | --- |
| `fopen` / `fprintf` / `fclose` / `fileread` | works |
| `save` / `load` round-trip through a `.mat` | works |
| `mkdir`, `dir`, `delete` | works |
| `rng(seed)` reproducibility for `rand` and `randn` | works |

Reproducible draws under a fixed seed are a precondition for Dynare's
Metropolis-Hastings estimation being verifiable at all, so this one is load-
bearing too.

Dynare has 11 `classdef` files and a large number of `+package` directories, so
this removes a whole category of risk. `@dprior` itself currently fails
`runmat check`, but on the definite-assignment rule above, not on anything to
do with being a class.

One gap, not a blocker: the *old* style of class directory — `@Box/Box.m`
containing a plain function that calls `class(o, 'Box')` — is not resolved
(`Undefined function: Box`). Dynare does not use that style anywhere, so it is
recorded rather than prioritized.

---

## Confirmed working

Worth recording, because it is a lot, and it means the gaps above are the
tractable kind:

Control flow (`for`, `while`, `if/elseif/else`, `try/catch`, short-circuit
`&&`/`||`), numeric `switch`, function handles and closures with correct capture
semantics, `varargin`/`varargout`/`nargin`/`nargout`, `persistent`, `global`,
recursion, local functions in scripts and multiple local functions per file,
cell arrays including `{end+1}` growth and comma-separated-list expansion
(`f(c{:})`), `cellfun` with and without `UniformOutput`, dynamic field names
`s.(f)`, `fieldnames`/`isfield`/`rmfield`/`getfield`/`setfield`, logical
indexing, `end` in ranges, deletion by `[]`, implicit expansion, `reshape`,
`permute`, `repmat`, multi-output `find`, `deal`, error identifiers with
`rethrow`, and most of `sprintf`.

---

## Suggested order of attack

Ordered by payoff per unit of work, not by severity alone.

1. **Alias `NaN(...)` / `Inf(...)` to `nan(...)` / `inf(...)`.** Smallest change
   on the list; unblocks 188 files and every failing runtime probe.
2. **Implement `filesep`** (and `ispc`/`isunix`/`ismac`/`computer`). `filesep`
   is a one-line function used in 118 Dynare files.
3. **Teach the definite-assignment checker about `global`.** One rule in the
   analysis; it is the largest single failure bucket and affects 123 files.
4. **Parser: accept unterminated functions.** One rule; unblocks ~80% of the
   files and makes every subsequent measurement meaningful.
5. **`switch` on strings.** Small, and it is everywhere in real MATLAB.
6. **Soften definite-assignment generally** — MATLAB has no such rule, so
   rejecting the program outright is stricter than the language allows. A
   warning would keep the diagnostic value without blocking valid code.
7. **Struct auto-vivification.** Larger semantic change, but Dynare's data model
   depends on it.
8. **QZ / `ordqz` / `schur`.** The gating item for solving anything. LAPACK
   already provides `dgges`/`dtgsen`; the work is binding and reordering, not
   numerics.
9. **Sparse `mtimes` / `mldivide`.**
10. Everything else in P2/P3 — individually small, mechanical.

Items 1-5 are, on the evidence here, a few days of work that would move Dynare
from "essentially unreadable" to "large parts load and run". Item 7 is the one
that decides whether a model can actually be solved, and it is real numerical
work rather than a compatibility patch.
