# Running real Dynare functions under RunMat

Functions taken from the shimmed Dynare tree, called with real inputs, compared against MATLAB's answer.

- Probes: **10**
- Passing: **7** (70.0%)

### ✅ `dynsec2hms`

- source: dynsec2hms.m

### ✅ `dynsec2hms_zero`

- source: dynsec2hms.m

### ❌ `dyn_vech`

- source: dyn_vech.m
- expected: `'1\n2\n3'`
- actual: `''`
- error:

```
error: Undefined function: NaN
id: RunMat:UndefinedFunction
callstack:
driver.m
```

### ❌ `dyn_unvech`

- source: dyn_unvech.m
- expected: `'1 2 2 3'`
- actual: `''`
- error:

```
error: Undefined function: NaN
id: RunMat:UndefinedFunction
--> driver.m:2:50
2 | fprintf('%d %d %d %d\n', M(1,1), M(1,2), M(2,1), M(2,2));
| ^^^^^^
callstack:
driver.m @ driver.m:2:50
```

### ❌ `vech_roundtrip`

- source: dyn_vech.m, dyn_unvech.m
- expected: `'1'`
- actual: `''`
- error:

```
error: Undefined function: NaN
id: RunMat:UndefinedFunction
--> driver.m:3:1
3 | fprintf('%d\n', isequal(A, B));
| ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
callstack:
driver.m @ driver.m:3:1
```

### ✅ `cellofchararraymaxlength`

- source: cellofchararraymaxlength.m

### ✅ `exactstrrep`

- source: exactstrrep.m

### ✅ `dynare_squeeze_row`

- source: dynare_squeeze.m

### ✅ `dynare_squeeze_col`

- source: dynare_squeeze.m

### ✅ `skipline`

- source: skipline.m

