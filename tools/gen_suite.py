#!/usr/bin/env python3
"""Author the conformance suite as real .m/.expected files.

Tests are defined here so a whole category can be added in a few lines, then
written out as ordinary files under tests/conformance/ that anyone can read,
run, or edit by hand. Re-running regenerates them.

`expected` is what MATLAB prints. Where a value is awkward to pin down as text
(a decomposition, a residual), the test asserts a mathematical identity and
prints 1 — property-based rather than format-dependent.

`xfail` marks a gap already confirmed against RunMat 0.6.2, with the reason.
The runner reports xfail separately from fail so a fix shows up as `xpass`.
"""

import os
import sys

# (category, name, code, expected, xfail_reason | None)
TESTS = [
    # ---------------------------------------------------------------- structs
    ("structs", "autoviv_scalar",
     "s.a = 1;\nfprintf('%d\\n', s.a);",
     "1",
     "RunMat requires the struct to exist before a field is assigned"),
    ("structs", "autoviv_nested",
     "s.a.b = 2;\nfprintf('%d\\n', s.a.b);",
     "2",
     "nested auto-vivification from an undefined base variable"),
    ("structs", "autoviv_after_struct",
     "s = struct();\ns.a.b = 3;\nfprintf('%d\\n', s.a.b);",
     "3", None),
    ("structs", "dynamic_fieldname_set",
     "s = struct();\nf = 'x';\ns.(f) = 9;\nfprintf('%d\\n', s.(f));",
     "9", None),
    ("structs", "fieldnames_order",
     "s = struct('b', 1, 'a', 2);\nf = fieldnames(s);\nfprintf('%s\\n', f{1}, f{2});",
     "b\na", None),
    ("structs", "isfield_and_rmfield",
     "s = struct('a', 1, 'b', 2);\ns = rmfield(s, 'a');\n"
     "fprintf('%d %d\\n', isfield(s, 'a'), isfield(s, 'b'));",
     "0 1", None),
    ("structs", "struct_array_numel",
     "s(1).a = 1;\ns(2).a = 2;\nfprintf('%d %d\\n', numel(s), s(2).a);",
     "2 2",
     "struct array built by indexed auto-vivification"),
    ("structs", "getfield_setfield",
     "s = struct('a', 1);\ns = setfield(s, 'a', 5);\nfprintf('%d\\n', getfield(s, 'a'));",
     "5", None),
    ("structs", "struct_passed_to_function",
     "o = struct('n', 4);\nfprintf('%d\\n', bump(o));\n"
     "function y = bump(o)\ny = o.n + 1;\nend",
     "5", None),
    ("structs", "struct_returned_modified",
     "o = struct('n', 1);\no = setn(o, 8);\nfprintf('%d\\n', o.n);\n"
     "function o = setn(o, v)\no.n = v;\nend",
     "8", None),

    # ------------------------------------------------------------------ cells
    ("cells", "cell_index_brace",
     "c = {1, 'two', [3 4]};\nfprintf('%s %d\\n', c{2}, numel(c{3}));",
     "two 2", None),
    ("cells", "cellfun_uniform_false",
     "c = {1, 2, 3};\nd = cellfun(@(x) x * 2, c, 'UniformOutput', false);\n"
     "fprintf('%d\\n', d{3});",
     "6", None),
    ("cells", "cellfun_uniform_true",
     "c = {1, 2, 3};\nv = cellfun(@(x) x * 2, c);\nfprintf('%d\\n', sum(v));",
     "12", None),
    ("cells", "cs_list_expansion",
     "c = {1, 2};\nfprintf('%d\\n', plus(c{:}));",
     "3", None),
    ("cells", "iscellstr_and_ismember",
     "c = {'aa', 'bb'};\nfprintf('%d %d\\n', iscellstr(c), ismember('bb', c));",
     "1 1", "ismember() rejects char/cellstr inputs, accepting only numeric or logical"),
    ("cells", "strjoin_strsplit",
     "p = strsplit('a,b,c', ',');\nfprintf('%s\\n', strjoin(p, '-'));",
     "a-b-c", "strjoin() cannot consume a cell array of strings"),
    ("cells", "cell_grow_by_index",
     "c = {};\nc{end+1} = 'x';\nc{end+1} = 'y';\nfprintf('%d %s\\n', numel(c), c{2});",
     "2 y", None),

    # -------------------------------------------------------------- functions
    ("functions", "nargin_default",
     "fprintf('%d\\n', f(1));\nfunction y = f(a, b)\nif nargin < 2\nb = 10;\nend\n"
     "y = a + b;\nend",
     "11", None),
    ("functions", "varargin_count",
     "fprintf('%d\\n', f(1, 2, 3));\nfunction n = f(varargin)\nn = numel(varargin);\nend",
     "3", None),
    ("functions", "varargout_two",
     "[a, b] = f();\nfprintf('%d %d\\n', a, b);\n"
     "function varargout = f()\nvarargout{1} = 1;\nvarargout{2} = 2;\nend",
     "1 2", None),
    ("functions", "nargout_aware",
     "[a, b] = f();\nfprintf('%d %d\\n', a, b);\n"
     "function [x, y] = f()\nx = nargout;\ny = 99;\nend",
     "2 99", None),
    ("functions", "anonymous_closure_capture",
     "k = 5;\ng = @(x) x + k;\nk = 100;\nfprintf('%d\\n', g(1));",
     "6", None),
    ("functions", "feval_by_name",
     "fprintf('%d\\n', feval(@max, 3, 7));",
     "7", None),
    ("functions", "str2func_roundtrip",
     "h = str2func('@(x) x * 3');\nfprintf('%d\\n', h(4));",
     "12", "str2func() does not evaluate an anonymous-function source string"),
    ("functions", "recursive_call",
     "fprintf('%d\\n', fact(5));\nfunction y = fact(n)\nif n <= 1\ny = 1;\nelse\n"
     "y = n * fact(n - 1);\nend\nend",
     "120", None),
    ("functions", "multiple_local_functions",
     "fprintf('%d\\n', a(2));\nfunction y = a(x)\ny = b(x) + 1;\nend\n"
     "function y = b(x)\ny = x * 10;\nend",
     "21", None),
    ("functions", "persistent_counter",
     "c();\nc();\nfprintf('%d\\n', c());\nfunction n = c()\npersistent k\n"
     "if isempty(k)\nk = 0;\nend\nk = k + 1;\nn = k;\nend",
     "3", None),
    ("functions", "global_shared",
     "global G\nG = 7;\nbump();\nfprintf('%d\\n', G);\n"
     "function bump()\nglobal G\nG = G + 1;\nend",
     "8", None),

    # ---------------------------------------------------------------- strings
    ("strings", "sprintf_float_formats",
     "fprintf('%5.3f|%e|%g\\n', 3.14159, 1234.5, 0.0001);",
     "3.142|1.234500e+03|0.0001", "%e prints 'e3' instead of MATLAB's signed 2-digit 'e+03' exponent"),
    ("strings", "num2str_default",
     "fprintf('%s %s\\n', num2str(3.5), num2str(42));",
     "3.5 42", None),
    ("strings", "str2double_and_nan",
     "fprintf('%d %d\\n', str2double('2.5') == 2.5, isnan(str2double('zz')));",
     "1 1", None),
    ("strings", "strrep_strtrim",
     "fprintf('[%s]\\n', strtrim(strrep('  a-b  ', '-', '+')));",
     "[a+b]", None),
    ("strings", "regexp_tokens",
     "t = regexp('x=12', '(\\\\w+)=(\\\\d+)', 'tokens');\n"
     "fprintf('%s %s\\n', t{1}{1}, t{1}{2});",
     "x 12", "regexp(...,'tokens') does not return MATLAB's nested cell structure"),
    ("strings", "regexprep_basic",
     "fprintf('%s\\n', regexprep('aaa', 'a', 'b', 'once'));",
     "baa", None),
    ("strings", "sprintf_vector_cycling",
     "fprintf('%d-', [1 2 3]);\nfprintf('\\n');",
     "1-2-3-", None),
    ("strings", "upper_lower_strcmpi",
     "fprintf('%s %d\\n', upper('ab'), strcmpi('AB', 'ab'));",
     "AB 1", None),

    # ----------------------------------------------------------------- linalg
    ("linalg", "backslash_square",
     "A = [4 1; 1 3];\nb = [1; 2];\nx = A \\ b;\nfprintf('%.4f\\n', x);",
     "0.0909\n0.6364", None),
    ("linalg", "eig_sorted",
     "d = sort(eig([2 0; 0 3]));\nfprintf('%.1f\\n', d);",
     "2.0\n3.0", None),
    ("linalg", "eig_identity_residual",
     "A = [4 1; 2 3];\n[V, D] = eig(A);\n"
     "fprintf('%d\\n', norm(A * V - V * D) < 1e-10);",
     "1", None),
    ("linalg", "chol_upper",
     "R = chol([4 2; 2 3]);\nfprintf('%d\\n', norm(R' * R - [4 2; 2 3]) < 1e-10);",
     "1", None),
    ("linalg", "svd_descending",
     "s = svd([3 0; 0 4]);\nfprintf('%.1f\\n', s);",
     "4.0\n3.0", None),
    ("linalg", "lu_residual",
     "A = [4 3; 6 3];\n[L, U, P] = lu(A);\n"
     "fprintf('%d\\n', norm(L * U - P * A) < 1e-10);",
     "1", None),
    ("linalg", "kron_shape",
     "K = kron([1 2], [1; 1]);\nfprintf('%d %d\\n', size(K, 1), size(K, 2));",
     "2 2", None),
    ("linalg", "norm_cond_rank",
     "fprintf('%.1f %d\\n', norm([3 4]), rank([1 2; 2 4]));",
     "5.0 1", None),
    ("linalg", "schur_decomposition",
     "A = [4 1; 2 3];\n[U, T] = schur(A);\n"
     "fprintf('%d\\n', norm(U * T * U' - A) < 1e-10);",
     "1",
     "schur() is not implemented in RunMat 0.6.2"),
    ("linalg", "qz_generalized_schur",
     "A = [4 1; 2 3];\nB = eye(2);\n[AA, BB, Q, Z] = qz(A, B);\n"
     "fprintf('%d\\n', norm(Q * A * Z - AA) < 1e-8);",
     "1",
     "qz() missing — this is Dynare's first-order perturbation solver"),
    ("linalg", "ordqz_reordering",
     "A = [4 1; 2 3];\nB = eye(2);\n[AA, BB, Q, Z] = qz(A, B);\n"
     "[~, ~, ~, Z2] = ordqz(AA, BB, Q, Z, 'udo');\n"
     "fprintf('%d\\n', size(Z2, 1));",
     "2",
     "ordqz() missing — required to split stable/unstable roots (Blanchard-Kahn)"),
    ("linalg", "expm_zero",
     "E = expm(zeros(2));\nfprintf('%d\\n', norm(E - eye(2)) < 1e-12);",
     "1",
     "expm() is not implemented in RunMat 0.6.2"),
    ("linalg", "sylvester_solve",
     "X = sylvester([1 0; 0 2], [3 0; 0 4], [1 1; 1 1]);\n"
     "fprintf('%d\\n', size(X, 1));",
     "2",
     "sylvester() missing — used for second-order solution terms"),
    ("linalg", "pinv_null",
     "fprintf('%d %d\\n', size(pinv([1 2; 2 4]), 1), size(null([1 2; 2 4]), 2));",
     "2 1", None),

    # ----------------------------------------------------------------- sparse
    ("sparse", "sparse_construct_full",
     "S = sparse([1 2], [2 1], [3 4], 2, 2);\nF = full(S);\n"
     "fprintf('%d %d %d\\n', F(1, 2), F(2, 1), nnz(S));",
     "3 4 2", None),
    ("sparse", "sparse_matmul",
     "S = sparse(eye(3));\nfprintf('%d\\n', norm(full(S * S) - eye(3)) < 1e-12);",
     "1", "mtimes() rejects sparse operands"),
    ("sparse", "issparse_speye",
     "fprintf('%d %d\\n', issparse(speye(2)), nnz(speye(3)));",
     "1 3", None),
    ("sparse", "sparse_backslash",
     "S = sparse([1 1; 0 1]);\nb = [2; 1];\nx = S \\ b;\n"
     "fprintf('%.1f\\n', x);",
     "1.0\n1.0", "mldivide() rejects sparse operands"),

    # ----------------------------------------------------------------- errors
    ("errors", "error_message_caught",
     "try\nerror('boom');\ncatch e\nfprintf('%s\\n', e.message);\nend",
     "boom", None),
    ("errors", "error_with_identifier",
     "try\nerror('My:id', 'text %d', 5);\ncatch e\n"
     "fprintf('%s|%s\\n', e.identifier, e.message);\nend",
     "My:id|text 5", None),
    ("errors", "mexception_construct",
     "try\nthrow(MException('A:b', 'msg'));\ncatch e\n"
     "fprintf('%s\\n', e.identifier);\nend",
     "A:b",
     "MException object construction/throw"),
    ("errors", "rethrow_preserves_id",
     "try\ntry\nerror('X:y', 'inner');\ncatch e1\nrethrow(e1);\nend\n"
     "catch e2\nfprintf('%s\\n', e2.identifier);\nend",
     "X:y", None),
    ("errors", "error_stack_field",
     "try\nerror('Q:r', 'z');\ncatch e\nfprintf('%d\\n', isfield(e, 'stack') || "
     "isprop(e, 'stack'));\nend",
     "1",
     "exception object exposing a stack field"),

    # ------------------------------------------------------------ indexing/etc
    ("indexing", "logical_indexing",
     "v = [1 2 3 4];\nfprintf('%d\\n', sum(v(v > 2)));",
     "7", None),
    ("indexing", "end_in_range",
     "v = 1:10;\nfprintf('%d %d\\n', v(end), numel(v(2:end-1)));",
     "10 8", None),
    ("indexing", "reshape_permute",
     "A = reshape(1:6, 2, 3);\nfprintf('%d %d\\n', A(2, 3), size(permute(A, [2 1]), 1));",
     "6 3", None),
    ("indexing", "repmat_and_colon",
     "R = repmat([1 2], 2, 1);\nfprintf('%d %d\\n', numel(R), sum(R(:)));",
     "4 6", None),
    ("indexing", "implicit_expansion",
     "A = [1 2] + [10; 20];\nfprintf('%d %d\\n', A(1, 1), A(2, 2));",
     "11 22", None),
    ("indexing", "deletion_by_empty",
     "v = 1:5;\nv(2) = [];\nfprintf('%d %d\\n', numel(v), v(2));",
     "4 3", None),
    ("indexing", "find_multiple_outputs",
     "[r, c] = find([0 1; 1 0]);\nfprintf('%d %d\\n', numel(r), sum(c));",
     "2 3", None),

    # ------------------------------------------------------------- platform
    # Written to be platform-agnostic: they assert the shape of the answer, not
    # a Linux-specific value, so the suite is portable.
    ("platform", "filesep_is_one_char",
     "s = filesep;\nfprintf('%d\\n', ischar(s) && numel(s) == 1);",
     "1",
     "filesep() is not implemented — used in 118 Dynare files"),
    ("platform", "pathsep_is_one_char",
     "s = pathsep;\nfprintf('%d\\n', ischar(s) && numel(s) == 1);",
     "1", None),
    ("platform", "exactly_one_platform_family",
     "fprintf('%d\\n', (ispc + isunix) >= 1);",
     "1",
     "ispc()/isunix() are not implemented"),
    ("platform", "ismac_is_logical",
     "fprintf('%d\\n', ismember(double(ismac), [0 1]));",
     "1",
     "ismac() is not implemented"),
    ("platform", "computer_returns_text",
     "fprintf('%d\\n', ischar(computer));",
     "1",
     "computer() is not implemented"),
    ("platform", "fullfile_and_fileparts",
     "p = fullfile('a', 'b', 'c.txt');\n[~, n, e] = fileparts(p);\n"
     "fprintf('%s%s\\n', n, e);",
     "c.txt", None),
    ("platform", "getenv_missing_is_empty",
     "fprintf('%d\\n', isempty(getenv('RUNMAT_DEFINITELY_NOT_SET_XYZ')));",
     "1", None),

    # --------------------------------------------------------- concatenation
    ("concat", "literal_matrix",
     "M = [1 2; 3 4];\nfprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "2 2", None),
    ("concat", "vertcat_two_row_vars",
     "a = [1 2];\nb = [3 4];\nM = [a; b];\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "2 2", None),
    ("concat", "vertcat_matrix_and_row",
     "A = [1 2; 3 4];\na = [5 6];\nM = [A; a];\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "3 2", None),
    ("concat", "horzcat_two_row_vars",
     "a = [1 2];\nb = [3 4];\nM = [a b];\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "1 4", None),
    ("concat", "vertcat_function_form",
     "a = [1 2];\nb = [3 4];\nM = vertcat(a, b);\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "2 2", None),
    ("concat", "var_row_then_literal_row",
     "a = [3 4];\nM = [a; 1 2];\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "2 2",
     "a bare variable row is counted as one column against a multi-element "
     "literal row"),
    ("concat", "literal_row_then_var_row",
     "a = [3 4];\nM = [1 2; a];\n"
     "fprintf('%d %d\\n', size(M, 1), size(M, 2));",
     "2 2",
     "a bare variable row is counted as one column against a multi-element "
     "literal row"),

    # -------------------------------------------------------------- complex
    # DSGE eigenvalues are generally complex, so this whole area is load-bearing
    # for any Blanchard-Kahn style stability check.
    ("complex", "complex_literal_parts",
     "z = 1 + 2i;\nfprintf('%d %d\\n', real(z), imag(z));",
     "1 2", None),
    ("complex", "complex_abs",
     "fprintf('%.1f\\n', abs(3 + 4i));",
     "5.0", None),
    ("complex", "complex_eig_imaginary",
     "d = eig([0 -1; 1 0]);\nfprintf('%.2f\\n', abs(imag(d(1))));",
     "1.00", None),
    ("complex", "complex_eig_modulus",
     "d = eig([0 -1; 1 0]);\nfprintf('%.2f\\n', abs(d(1)));",
     "1.00", None),
    ("complex", "count_roots_outside_unit_circle",
     "A = [2 0; 0 0.5];\nd = eig(A);\nfprintf('%d\\n', sum(abs(d) > 1));",
     "1", None),
    ("complex", "conj_and_angle",
     "fprintf('%.2f %.4f\\n', real(conj(1 + 2i)), angle(1i));",
     "1.00 1.5708", None),
    ("complex", "sqrt_of_negative",
     "fprintf('%.2f\\n', imag(sqrt(-4)));",
     "2.00", None),
    ("complex", "complex_matrix_product",
     "A = [1i 0; 0 1i];\nB = A * A;\nfprintf('%d\\n', real(B(1, 1)));",
     "-1", None),

    # ------------------------------------------------------- printf formats
    ("printf", "g_whole_number",
     "fprintf('[%g]\\n', 1);",
     "[1]",
     "%g emits a trailing '.' on whole numbers — prints '1.'"),
    ("printf", "g_large_whole",
     "fprintf('[%g]\\n', 100000);",
     "[100000]",
     "%g emits a trailing '.' — prints '100000.'"),
    ("printf", "g_small_exponent",
     "fprintf('[%g]\\n', 0.00001);",
     "[1e-05]",
     "%g prints '1.00000e-5': keeps trailing zeros and omits the "
     "two-digit exponent padding"),
    ("printf", "g_decimal",
     "fprintf('[%g]\\n', 2.5);",
     "[2.5]", None),
    ("printf", "e_exponent_padding",
     "fprintf('[%e]\\n', 1234.5);",
     "[1.234500e+03]",
     "%e prints 'e3' instead of the signed two-digit 'e+03'"),
    # No field width here: the runner collapses whitespace, so a padded
    # expectation could not be checked honestly.
    ("printf", "f_precision",
     "fprintf('[%.3f]\\n', 3.14159);",
     "[3.142]", None),
    ("printf", "mat2str_roundtrip",
     "fprintf('%s\\n', mat2str([1 2; 3 4]));",
     "[1 2;3 4]", None),

    # --------------------------------------------------------- constructors
    ("constructors", "nan_lowercase_sized",
     "fprintf('%d %d\\n', size(nan(2, 3), 1), size(nan(2, 3), 2));",
     "2 3", None),
    ("constructors", "NaN_capitalized_sized",
     "fprintf('%d %d\\n', size(NaN(2, 3), 1), size(NaN(2, 3), 2));",
     "2 3",
     "NaN(...) is not callable as a constructor though nan(...) is; "
     "188 Dynare files use the capitalized spelling"),
    ("constructors", "Inf_capitalized_sized",
     "fprintf('%d\\n', size(Inf(2, 2), 1));",
     "2",
     "Inf(...) is not callable as a constructor though inf(...) is"),
    ("constructors", "NaN_bare_constant",
     "fprintf('%d\\n', isnan(NaN));",
     "1", None),
    ("constructors", "zeros_ones_true_cell",
     "fprintf('%d %d %d %d\\n', size(zeros(2, 3), 2), size(ones(2), 1), "
     "size(true(2), 1), size(cell(2), 1));",
     "3 2 2 2", None),

    # ------------------------------------------------------------------ misc
    ("misc", "switch_on_string",
     "x = 'b';\nswitch x\ncase 'a'\nfprintf('A\\n');\ncase 'b'\nfprintf('B\\n');\n"
     "otherwise\nfprintf('O\\n');\nend",
     "B", "switch on a char value coerces the operand to f64 and errors"),
    ("misc", "switch_cell_case",
     "x = 'c';\nswitch x\ncase {'b', 'c'}\nfprintf('BC\\n');\notherwise\n"
     "fprintf('O\\n');\nend",
     "BC", "switch on a char value coerces the operand to f64 and errors"),
    ("misc", "exist_variable_vs_builtin",
     "zz = 1;\nfprintf('%d %d\\n', exist('zz', 'var'), exist('nosuchthing', 'var'));",
     "1 0", None),
    ("misc", "eval_simple",
     "eval('w = 6;');\nfprintf('%d\\n', w);",
     "6", "eval() does not create the variable in the caller's scope"),
    ("misc", "inputname_free_call",
     "fprintf('%d\\n', isempty(''));",
     "1", None),
    ("misc", "isa_and_class",
     "fprintf('%s %d\\n', class(1), isa('s', 'char'));",
     "double 1", None),
    ("misc", "deal_multiple",
     "[a, b] = deal(1, 2);\nfprintf('%d %d\\n', a, b);",
     "1 2", None),
    ("misc", "num_to_logical_short_circuit",
     "x = 0;\nif x ~= 0 && (1 / x) > 1\nfprintf('bad\\n');\nelse\nfprintf('ok\\n');\nend",
     "ok", None),
]


def main() -> int:
    out_root = sys.argv[1] if len(sys.argv) > 1 else "tests/conformance"
    n = 0
    for category, name, code, expected, xfail in TESTS:
        d = os.path.join(out_root, category)
        os.makedirs(d, exist_ok=True)
        header = f"%% xfail: {xfail}\n" if xfail else ""
        with open(os.path.join(d, name + ".m"), "w") as fh:
            fh.write(header + code.rstrip() + "\n")
        with open(os.path.join(d, name + ".expected"), "w") as fh:
            fh.write(expected.rstrip() + "\n")
        n += 1
    print(f"wrote {n} conformance cases to {out_root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
