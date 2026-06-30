import base64
import io
from types import SimpleNamespace

from django.template import Context, Template
from PIL import Image
import pytest

from hope.apps.registration_data.templatetags.smart_register import (
    concat,
    dump,
    dump_dict,
    dump_list,
    is_base64,
    is_image,
    isdict,
    islist,
    isstring,
    lookup,
    smart_attr,
)


@pytest.fixture
def png_base64() -> str:
    # deterministic noise so the PNG does not compress below the 200-char minimum
    data = bytes((i * 7) % 256 for i in range(64 * 64 * 3))
    buffer = io.BytesIO()
    Image.frombytes("RGB", (64, 64), data).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


@pytest.mark.parametrize(
    ("value", "expected"),
    [([1, 2], True), ((1, 2), True), ("ab", False), ({"a": 1}, False)],
)
def test_islist(value: object, expected: bool) -> None:
    assert islist(value) is expected


@pytest.mark.parametrize(("value", "expected"), [("ab", True), (1, False), ([], False)])
def test_isstring(value: object, expected: bool) -> None:
    assert isstring(value) is expected


@pytest.mark.parametrize(("value", "expected"), [({"a": 1}, True), ("ab", False), ([], False)])
def test_isdict(value: object, expected: bool) -> None:
    assert isdict(value) is expected


def test_dump_returns_value_key_original() -> None:
    assert dump("v", "k", "o") == {"value": "v", "key": "k", "original": "o"}


def test_dump_list_returns_value_key_original() -> None:
    assert dump_list("v") == {"value": "v", "key": None, "original": None}


def test_dump_dict_returns_value_key_original() -> None:
    assert dump_dict("v", key="k") == {"value": "v", "key": "k", "original": None}


def test_smart_attr_reads_nested_smart_mapping() -> None:
    field = SimpleNamespace(field=SimpleNamespace(flex_field=SimpleNamespace(advanced={"smart": {"hint": "ok"}})))

    assert smart_attr(field, "hint") == "ok"


def test_smart_attr_missing_attr_returns_empty_string() -> None:
    field = SimpleNamespace(field=SimpleNamespace(flex_field=SimpleNamespace(advanced={"smart": {}})))

    assert smart_attr(field, "hint") == ""


def test_lookup_returns_value_for_key() -> None:
    assert lookup({"a": 1}, "a") == 1


def test_lookup_missing_key_returns_none() -> None:
    assert lookup({"a": 1}, "b") is None


def test_concat_stringifies_and_joins() -> None:
    assert concat(1, "b") == "1b"


def test_is_image_true_for_real_png(png_base64: str) -> None:
    assert is_image(png_base64) is True


@pytest.mark.parametrize(
    "element",
    [123, "short", "x" * 250 + "ł"],
    ids=["not-a-string", "too-short", "non-ascii"],
)
def test_is_image_false_for_invalid_input(element: object) -> None:
    assert is_image(element) is False


def test_is_image_false_when_not_an_image() -> None:
    not_image = base64.b64encode(b"a" * 200).decode("ascii")

    assert is_image(not_image) is False


def test_is_base64_true_for_padded_base64() -> None:
    # single byte -> double "=" padding, which is what the filter looks for
    assert is_base64(base64.b64encode(b"a").decode("ascii")) is True


@pytest.mark.parametrize("element", ["not-base64", 123, "abcd"], ids=["no-padding", "not-string", "no-double-eq"])
def test_is_base64_false(element: object) -> None:
    assert is_base64(element) is False


def test_escapescript_tag_escapes_closing_script_tag() -> None:
    template = Template("{% load smart_register %}{% escapescript %}</script>{% endescapescript %}")

    assert template.render(Context({})) == "<\\/script>"
