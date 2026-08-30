# RunMat semantic conformance (Dynare-relevant features)

- Cases: **74**
- Working (pass + xpass): **54** (72.97%)
- Failing: **10**, known gaps (xfail): **10**

## By category

### cells — 5/7

- 🎉 `cells/cs_list_expansion` comma-separated list expansion of c{:} into function arguments
- ❌ `cells/iscellstr_and_ismember` 
- ❌ `cells/strjoin_strsplit` 

### errors — 3/5

- ⚠️ `errors/error_stack_field` exception object exposing a stack field
- ⚠️ `errors/mexception_construct` MException object construction/throw

### functions — 10/11

- ❌ `functions/str2func_roundtrip` 

### indexing — 7/7


### linalg — 9/14

- ⚠️ `linalg/expm_zero` expm() is not implemented in RunMat 0.6.2
- ⚠️ `linalg/ordqz_reordering` ordqz() missing — required to split stable/unstable roots (Blanchard-Kahn)
- ⚠️ `linalg/qz_generalized_schur` qz() missing — this is Dynare's first-order perturbation solver
- ⚠️ `linalg/schur_decomposition` schur() is not implemented in RunMat 0.6.2
- ⚠️ `linalg/sylvester_solve` sylvester() missing — used for second-order solution terms

### misc — 5/8

- ❌ `misc/eval_simple` 
- ❌ `misc/switch_cell_case` 
- ❌ `misc/switch_on_string` 

### sparse — 2/4

- ❌ `sparse/sparse_backslash` 
- ❌ `sparse/sparse_matmul` 

### strings — 6/8

- ❌ `strings/regexp_tokens` 
- ❌ `strings/sprintf_float_formats` 

### structs — 7/10

- ⚠️ `structs/autoviv_nested` nested auto-vivification from an undefined base variable
- ⚠️ `structs/autoviv_scalar` RunMat requires the struct to exist before a field is assigned
- ⚠️ `structs/struct_array_numel` struct array built by indexed auto-vivification

