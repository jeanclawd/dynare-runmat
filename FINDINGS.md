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

## P2 — missing builtins Dynare depends on

### 6. The QZ family is absent — this blocks model solution outright

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

### 7. Sparse matrices exist but core operations reject them

```matlab
S = sparse(eye(3));
S * S      % error: mtimes: unsupported operand types
S \ [1;2]  % error: mldivide: unsupported input type SparseTensor
```

Construction, `full`, `nnz`, `issparse`, and `speye` all work — the type is
there, the operations are not. Dynare represents Jacobians sparsely throughout.

### 8. `ismember` rejects char and cellstr

```matlab
ismember('bb', {'aa', 'bb'})
% error: ismember: unsupported input type CharArray; expected numeric or logical
```

### 9. `strjoin` cannot consume a cell array of strings

```matlab
strjoin(strsplit('a,b,c', ','), '-')
% error: cannot convert to string array: Cell(CellArray { ... })
```

`strsplit` produces the cell array correctly; `strjoin` will not take it back.

---

## P3 — output and detail differences

### 10. `%e` produces a malformed exponent

```matlab
fprintf('%e\n', 1234.5)
```

| | |
| --- | --- |
| MATLAB | `1.234500e+03` |
| RunMat | `1.234500e3` |

Missing both the exponent sign and the two-digit zero padding. This silently
changes any Dynare output, log file, or result table that uses `%e`.

### 11. `regexp(..., 'tokens')` returns the wrong nesting

```matlab
t = regexp('x=12', '(\w+)=(\d+)', 'tokens');
t{1}{2}    % error: Cell index out of bounds
```

MATLAB returns a cell of matches, each itself a cell of that match's tokens.
RunMat's shape differs, so the standard `t{i}{j}` access fails.

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

1. **Parser: accept unterminated functions.** One rule; unblocks ~80% of the
   files and makes every subsequent measurement meaningful.
2. **`switch` on strings.** Small, and it is everywhere in real MATLAB.
3. **Struct auto-vivification.** Larger semantic change, but Dynare's data model
   depends on it.
4. **QZ / `ordqz` / `schur`.** The gating item for solving anything. LAPACK
   already provides `dgges`/`dtgsen`; the work is binding and reordering, not
   numerics.
5. **Sparse `mtimes` / `mldivide`.**
6. Everything in P2/P3 — individually small, mechanical.
