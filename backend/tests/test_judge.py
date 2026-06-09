from judge import run_python_code


class TestRunPythonCode:
    """Tests for the judge.run_python_code function."""

    def test_valid_code_accepted(self):
        result = run_python_code("x = 1 + 2")
        assert result["verdict"] == "Accepted"
        assert result["score"] == 100
        assert result["runtime_ms"] >= 0

    def test_valid_function_definition(self):
        code = "def solve(a, b):\n    return a + b"
        result = run_python_code(code)
        assert result["verdict"] == "Accepted"
        assert result["score"] == 100

    def test_empty_code_accepted(self):
        result = run_python_code("")
        assert result["verdict"] == "Accepted"

    def test_syntax_error_compilation_error(self):
        result = run_python_code("def foo(")
        assert result["verdict"] == "Compilation Error"
        assert result["score"] == 0
        assert result["runtime_ms"] == 0
        assert "error" in result

    def test_indentation_error(self):
        code = "def foo():\nreturn 1"
        result = run_python_code(code)
        assert result["verdict"] == "Compilation Error"
        assert result["score"] == 0

    def test_multiline_valid_code(self):
        code = (
            "import math\n"
            "def solve(n):\n"
            "    return math.factorial(n)\n"
        )
        result = run_python_code(code)
        assert result["verdict"] == "Accepted"

    def test_runtime_ms_is_integer(self):
        result = run_python_code("pass")
        assert isinstance(result["runtime_ms"], int)

    def test_compilation_error_has_message(self):
        result = run_python_code("+++")
        assert result["verdict"] == "Compilation Error"
        assert len(result["error"]) > 0
