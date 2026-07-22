from django.core.exceptions import ValidationError
import pytest

from hope.apps.steficon.exception import RuleError
from hope.apps.steficon.interpreters import Interpreter, PythonExec, mapping


class PassingInterpreter(Interpreter):
    def execute(self) -> bool:
        return True


class FailingInterpreter(Interpreter):
    def execute(self) -> bool:
        raise RuleError(rule=self, error_class="TypeError", detail="boom", line_number=1)


def test_interpreter_validate_returns_true_when_execute_succeeds():
    interpreter = PassingInterpreter("result.value = 1")

    assert interpreter.validate() is True


def test_interpreter_validate_wraps_rule_error_in_validation_error():
    interpreter = FailingInterpreter("result.value = 1")

    with pytest.raises(ValidationError, match="TypeError: boom at 1"):
        interpreter.validate()


def test_python_exec_code_compiles_init_string():
    interpreter = PythonExec("result.value = 1")

    assert interpreter.code is not None


def test_python_exec_execute_returns_result_with_assigned_value():
    interpreter = PythonExec("result.value = 42")

    result = interpreter.execute({})

    assert result.value == 42


def test_python_exec_execute_raises_rule_error_on_syntax_error():
    interpreter = PythonExec("result.value = (")

    with pytest.raises(RuleError) as exc_info:
        interpreter.execute({})

    assert exc_info.value.error_class == "SyntaxError"


def test_python_exec_execute_raises_rule_error_on_zero_division():
    interpreter = PythonExec("result.value = 1 / 0")

    with pytest.raises(RuleError) as exc_info:
        interpreter.execute({})

    assert exc_info.value.error_class == "ZeroDivisionError"


def test_python_exec_validate_returns_true_for_valid_code():
    interpreter = PythonExec("result.value = 1")

    assert interpreter.validate() is True


def test_python_exec_validate_raises_on_forbidden_word():
    interpreter = PythonExec("result.value = eval('1')")

    with pytest.raises(ValidationError, match="Code contains an invalid statement 'eval'"):
        interpreter.validate()


def test_python_exec_validate_raises_on_syntax_error():
    interpreter = PythonExec("result.value = (")

    with pytest.raises(ValidationError, match="never closed"):
        interpreter.validate()


def test_mapping_contains_python_exec():
    assert mapping["python"] is PythonExec
