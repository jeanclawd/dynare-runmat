# RunMat parse sweep over Dynare

- Files scanned: **1056**
- Parsed clean: **294** (27.84%)
- Failed: **762**

## Failures by error id

- `Unknown` — 488
- `RunMat:UndefinedVariable` — 186
- `RunMat:ParseError` — 61
- `RunMat:AggregateShapeMismatch` — 12
- `RunMat:MirLoweringError` — 7
- `RunMat:MirCallFallbackPolicyUnsupported` — 4
- `RunMat:MirParallelCapabilityUnsupported` — 3
- `RunMat:MirCallTargetNameInvalid` — 1

## Top failure signatures

- 212 x — Unknown | local may be read before it is assigned
- 186 x — RunMat:UndefinedVariable | undefined variable 'X'
- 143 x — Unknown | local may be read before assignment on some control-flow paths
- 88 x — Unknown | brace indexing requires a cell-like value
- 35 x — Unknown | 
- 20 x — RunMat:ParseError | expected 'X'
- 13 x — RunMat:ParseError | expected identifier
- 12 x — RunMat:AggregateShapeMismatch | tensor literal rows must have consistent column counts
- 8 x — RunMat:ParseError | expected identifier or 'X'
- 7 x — RunMat:MirLoweringError | feval: function argument cannot be a comma-list expansion
- 4 x — RunMat:ParseError | expected 'X' to close cell literal
- 3 x — Unknown | index for dimension N is outside the proven bound N
- 3 x — RunMat:MirCallFallbackPolicyUnsupported | local may be read before it is assigned
- 3 x — RunMat:ParseError | unexpected token: Minus
- 3 x — RunMat:MirParallelCapabilityUnsupported | parallel-region MIR requires the structured scheduler lowering capability
- 2 x — RunMat:ParseError | unexpected token: RBrace
- 2 x — RunMat:ParseError | unexpected token: RBracket
- 2 x — RunMat:ParseError | unexpected token: Newline
- 2 x — Unknown | operator is not defined for the proven operand value category
- 1 x — RunMat:ParseError | Syntax error at position N: expected 'X' to close cell literal (found: 'X'='X') (expected: 'X')
- 1 x — RunMat:ParseError | Syntax error at position N: expected 'X' to close cell literal (found: 'X'idbeta'X') (expected: 'X')
- 1 x — Unknown | right-division column dimensions N and N do not agree
- 1 x — Unknown | transpose requires a numeric, logical, or character value
- 1 x — RunMat:MirCallFallbackPolicyUnsupported | MIR workspace-first call fallback policy None is not supported for static callee BoundFunction(Funct
- 1 x — RunMat:ParseError | 'X' command syntax accepts only one argument; found `
