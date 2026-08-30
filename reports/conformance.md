# RunMat semantic conformance (Dynare-relevant features)

- Cases: **99**
- Working (pass + xpass): **73** (73.74%)
- Failing: **0**, known gaps (xfail): **26**

## By category

### cells — 5/7

- ⚠️ `cells/iscellstr_and_ismember` ismember() rejects char/cellstr inputs, accepting only numeric or logical
- ⚠️ `cells/strjoin_strsplit` strjoin() cannot consume a cell array of strings

### complex — 8/8


### constructors — 3/5

- ⚠️ `constructors/Inf_capitalized_sized` Inf(...) is not callable as a constructor though inf(...) is
- ⚠️ `constructors/NaN_capitalized_sized` NaN(...) is not callable as a constructor though nan(...) is; 188 Dynare files use the capitalized spelling

### errors — 3/5

- ⚠️ `errors/error_stack_field` exception object exposing a stack field
- ⚠️ `errors/mexception_construct` MException object construction/throw

### functions — 10/11

- ⚠️ `functions/str2func_roundtrip` str2func() does not evaluate an anonymous-function source string

### indexing — 7/7


### linalg — 9/14

- ⚠️ `linalg/expm_zero` expm() is not implemented in RunMat 0.6.2
- ⚠️ `linalg/ordqz_reordering` ordqz() missing — required to split stable/unstable roots (Blanchard-Kahn)
- ⚠️ `linalg/qz_generalized_schur` qz() missing — this is Dynare's first-order perturbation solver
- ⚠️ `linalg/schur_decomposition` schur() is not implemented in RunMat 0.6.2
- ⚠️ `linalg/sylvester_solve` sylvester() missing — used for second-order solution terms

### misc — 5/8

- ⚠️ `misc/eval_simple` eval() does not create the variable in the caller's scope
- ⚠️ `misc/switch_cell_case` switch on a char value coerces the operand to f64 and errors
- ⚠️ `misc/switch_on_string` switch on a char value coerces the operand to f64 and errors

### multifile — 5/5


### printf — 3/7

- ⚠️ `printf/e_exponent_padding` %e prints 'e3' instead of the signed two-digit 'e+03'
- ⚠️ `printf/g_large_whole` %g emits a trailing '.' — prints '100000.'
- ⚠️ `printf/g_small_exponent` %g prints '1.00000e-5': keeps trailing zeros and omits the two-digit exponent padding
- ⚠️ `printf/g_whole_number` %g emits a trailing '.' on whole numbers — prints '1.'

### sparse — 2/4

- ⚠️ `sparse/sparse_backslash` mldivide() rejects sparse operands
- ⚠️ `sparse/sparse_matmul` mtimes() rejects sparse operands

### strings — 6/8

- ⚠️ `strings/regexp_tokens` regexp(...,'tokens') does not return MATLAB's nested cell structure
- ⚠️ `strings/sprintf_float_formats` %e prints 'e3' instead of MATLAB's signed 2-digit 'e+03' exponent

### structs — 7/10

- ⚠️ `structs/autoviv_nested` nested auto-vivification from an undefined base variable
- ⚠️ `structs/autoviv_scalar` RunMat requires the struct to exist before a field is assigned
- ⚠️ `structs/struct_array_numel` struct array built by indexed auto-vivification

