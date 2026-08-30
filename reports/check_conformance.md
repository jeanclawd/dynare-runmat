# Valid MATLAB that `runmat check` rejects

Every case here is legal MATLAB. `runs correctly: True` means the code executes and returns MATLAB's answer, so the rejection is the checker's and not the code's. `False` means the gap is in the runtime too, not only in `runmat check`.

- Cases: **6**
- Check clean: **1**
- Known checker gaps (xfail): **5**
- Unexpected: **0**

### ⚠️ `brace_index_parameter`

- gap: brace indexing a parameter is refused because RunMat cannot prove it is a cell
- `error[RM-TYPE-BRACE-INDEX]: brace indexing requires a cell-like value`
- runs correctly: **True** (expected `20`, got `20`)

### ⚠️ `branch_assigned_local`

- gap: definite assignment rejects a local assigned in one branch and read after
- `error[RM-MIR0002]: local may be read before assignment on some control-flow paths`
- runs correctly: **True** (expected `1`, got `1`)

### ⚠️ `feval_comma_list`

- gap: feval(fs{i}, ...) is refused at check AND at run time — a brace index is treated as a comma-list expansion even with a scalar index
- `error[RunMat:MirLoweringError]: feval: function argument cannot be a comma-list expansion`
- runs correctly: **False** (expected `7`, got ``)

### ⚠️ `global_read`

- gap: the definite-assignment analysis does not treat `global` as bringing the name into scope
- `error[RM-MIR0001]: local may be read before it is assigned`
- runs correctly: **True** (expected `42`, got `42`)

### ⚠️ `nested_if_param_reassign_index`

- gap: stack overflow — a parameter reassigned in a nested if, then used as an index, crashes check AND run
- runs correctly: **False** (expected `7`, got ``)

### ✅ `plain_function`

- runs correctly: **True** (expected `5`, got `5`)

