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
    # The salutation must never produce a stray space when a name part is missing
    # (e.g. "Dear ,") — that is the whole reason this tag exists.
    assert greeting(first_name, last_name) == expected
