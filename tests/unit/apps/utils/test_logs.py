import logging

from hope.apps.utils.logs import LogForgingFilter, _SanitizedValue, safe_log


def test_sanitized_value_str_strips_newline() -> None:
    assert str(_SanitizedValue("line1\nline2")) == "line1line2"


def test_sanitized_value_str_strips_carriage_return() -> None:
    assert str(_SanitizedValue("line1\rline2")) == "line1line2"


def test_sanitized_value_repr_strips_newline() -> None:
    assert "\n" not in repr(_SanitizedValue("a\nb"))


def test_sanitized_value_str_passthrough_clean_value() -> None:
    assert str(_SanitizedValue("clean")) == "clean"


def test_log_forging_filter_sanitizes_tuple_args() -> None:
    record = logging.LogRecord(
        name="test", level=logging.WARNING, pathname="", lineno=0,
        msg="user %s action %s", args=("evil\nINJECTED", "also\rbad"), exc_info=None,
    )
    f = LogForgingFilter()
    assert f.filter(record) is True
    assert isinstance(record.args, tuple)
    assert str(record.args[0]) == "evilINJECTED"
    assert str(record.args[1]) == "alsобad".replace("о", "o")  # plain ascii check
    assert "\n" not in str(record.args[0])
    assert "\r" not in str(record.args[1])


def test_log_forging_filter_sanitizes_dict_args() -> None:
    record = logging.LogRecord(
        name="test", level=logging.WARNING, pathname="", lineno=0,
        msg="%(key)s", args={"key": "evil\nvalue"}, exc_info=None,
    )
    f = LogForgingFilter()
    assert f.filter(record) is True
    assert isinstance(record.args, dict)
    assert "\n" not in str(record.args["key"])
    assert str(record.args["key"]) == "evilvalue"


def test_log_forging_filter_no_args_passes_through() -> None:
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="static message", args=None, exc_info=None,
    )
    f = LogForgingFilter()
    assert f.filter(record) is True
    assert record.args is None


def test_log_forging_filter_preserves_hardcoded_template_newlines() -> None:
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0,
        msg="line1\nline2 %s", args=("clean",), exc_info=None,
    )
    f = LogForgingFilter()
    f.filter(record)
    assert "\n" in record.msg


def test_safe_log_strips_cr_lf() -> None:
    assert safe_log("a\nb\rc") == "abc"


def test_safe_log_passthrough_clean() -> None:
    assert safe_log("hello") == "hello"


def test_safe_log_non_string_coerced() -> None:
    assert safe_log(42) == "42"
