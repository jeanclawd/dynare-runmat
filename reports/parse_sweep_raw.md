# RunMat parse sweep over Dynare

- Files scanned: **1056**
- Parsed clean: **63** (5.97%)
- Failed: **993**

## Failures by error id

- `RunMat:ParseError` — 835
- `Unknown` — 106
- `RunMat:UndefinedVariable` — 42
- `RunMat:MirLoweringError` — 6
- `RunMat:AggregateShapeMismatch` — 2
- `RunMat:MirCallFallbackPolicyUnsupported` — 2

## Top failure signatures

- 794 x — RunMat:ParseError | expected 'X'
- 42 x — Unknown | local may be read before it is assigned
- 42 x — RunMat:UndefinedVariable | undefined variable 'X'
- 31 x — Unknown | brace indexing requires a cell-like value
- 16 x — Unknown | local may be read before assignment on some control-flow paths
- 15 x — Unknown | 
- 13 x — RunMat:ParseError | expected identifier
- 8 x — RunMat:ParseError | expected identifier or 'X'
- 6 x — RunMat:MirLoweringError | feval: function argument cannot be a comma-list expansion
- 4 x — RunMat:ParseError | expected 'X' to close cell literal
- 3 x — RunMat:ParseError | unexpected token: Minus
- 2 x — RunMat:AggregateShapeMismatch | tensor literal rows must have consistent column counts
- 2 x — RunMat:ParseError | unexpected token: RBrace
- 2 x — RunMat:MirCallFallbackPolicyUnsupported | local may be read before it is assigned
- 2 x — RunMat:ParseError | unexpected token: RBracket
- 2 x — RunMat:ParseError | unexpected token: Newline
- 1 x — Unknown | index for dimension N is outside the proven bound N
- 1 x — RunMat:ParseError | Syntax error at position N: expected 'X' to close cell literal (found: 'X'='X') (expected: 'X')
- 1 x — RunMat:ParseError | Syntax error at position N: expected 'X' to close cell literal (found: 'X'idbeta'X') (expected: 'X')
- 1 x — Unknown | operator is not defined for the proven operand value category
- 1 x — RunMat:ParseError | 'X' command syntax accepts only one argument; found `
- 1 x — RunMat:ParseError | expected multi-assignment target
- 1 x — RunMat:ParseError | Syntax error at position N: expected member name after 'X' (found: 'X') (expected: identifier)
- 1 x — RunMat:ParseError | Unexpected adjacency: interpret as function call? Use parentheses (e.g., foo(b(N))).
- 1 x — RunMat:ParseError | Syntax error at position N: expected 'X' to close cell literal (found: 'X') (expected: 'X')
