import pytest

from extras.test_utils.factories.steficon import RuleFactory
from hope.apps.steficon.templatetags.jsonfy import _jsonfy, _repr, pretty_json, pretty_python, smart_json


@pytest.fixture
def rule():
    return RuleFactory(name="Test Rule", definition="result.value = 100")


def test_jsonfy_scalar_returns_string():
    assert _jsonfy(100) == "100"


def test_jsonfy_nested_dict_returns_dict_of_strings():
    assert _jsonfy({"outer": {"inner": 1}}) == {"outer": {"inner": "1"}}


def test_jsonfy_deeply_nested_dict_does_not_recurse_infinitely():
    assert _jsonfy({"a": {"b": {"c": "leaf"}}}) == {"a": {"b": {"c": "leaf"}}}


@pytest.mark.django_db
def test_jsonfy_model_returns_serialized_fields(rule):
    result = _jsonfy(rule)

    assert result[0]["fields"]["name"] == "Test Rule"


def test_pretty_json_dict_with_nested_dict_renders_inner_value():
    result = pretty_json({"payload": {"score": 5}})

    assert "score" in result
    assert "highlight" in result


def test_pretty_json_non_dict_wraps_value_with_type():
    result = pretty_json("plain")

    assert "plain" in result
    assert "str" in result


def test_smart_json_non_model_renders_mapping():
    result = smart_json({"key": "value"})

    assert "value" in result


@pytest.mark.django_db
def test_smart_json_model_renders_serialized_fields(rule):
    result = smart_json(rule)

    assert "Test Rule" in result


def test_pretty_python_highlights_source():
    result = pretty_python("result.value = 1")

    assert "highlight" in result


def test_repr_returns_python_representation():
    assert _repr("abc") == "'abc'"
