import pytest

from hope.models.individual import normalize_latin_name


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        ("", ""),
        ("Anna Kovalska", "Anna Kovalska"),
        ("  Anna Kovalska  ", "Anna Kovalska"),
        ("Anna   Kovalska", "Anna Kovalska"),
        ("Anna\nKovalska", "Anna Kovalska"),
        ("Anna\tKovalska", "Anna Kovalska"),
        ("Anna\xa0Kovalska", "Anna Kovalska"),
    ],
)
def test_normalize_latin_name(value: str | None, expected: str | None) -> None:
    assert normalize_latin_name(value) == expected
