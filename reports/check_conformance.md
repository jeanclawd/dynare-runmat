# Valid MATLAB that `runmat check` rejects

Every case here is legal MATLAB. Cases marked `runs` are also confirmed to execute correctly, so a rejection is the checker's, not the code's.

- Cases: **4**
- Check clean: **1**
- Known checker gaps (xfail): **3**
- Unexpected: **0**

### ⚠️ `brace_index_parameter`

- gap: brace indexing a parameter is refused because RunMat cannot prove it is a cell
- `error[RM-TYPE-BRACE-INDEX]: brace indexing requires a cell-like value`
- runs correctly: **True** (expected `20`, got `20`)

### ⚠️ `branch_assigned_local`

- gap: definite assignment rejects a local assigned in one branch and read after
- `error[RM-MIR0002]: local may be read before assignment on some control-flow paths`
- runs correctly: **True** (expected `1`, got `1`)

### ⚠️ `global_read`

- gap: the definite-assignment analysis does not treat `global` as bringing the name into scope
- `error[RM-MIR0001]: local may be read before it is assigned`
- runs correctly: **True** (expected `42`, got `42`)

### ✅ `plain_function`

- runs correctly: **True** (expected `5`, got `5`)

