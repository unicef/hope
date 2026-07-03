import pytest

from hope.apps.utils.templatetags.custom_tags import greeting


@pytest.mark.parametrize(
    ("first_name", "last_name", "expected"),
    [
        ("John", "Doe", "Dear John Doe,"),
        ("John", "", "Dear John,"),
        ("", "Doe", "Dear Doe,"),
        ("", "", "Dear,"),
        ("John", None, "Dear John,"),
        (None, None, "Dear,"),
    ],
)
def test_greeting(first_name: str | None, last_name: str | None, expected: str) -> None:
    assert greeting(first_name, last_name) == expected
