from hope.contrib.aurora.services.generic_registration_service import mergedicts


def test_mergedicts_returns_first_when_second_is_none() -> None:
    result = mergedicts({"a": 1, "b": 2}, None, [])

    assert result == {"a": 1, "b": 2}


def test_mergedicts_returns_first_when_second_is_empty() -> None:
    result = mergedicts({"a": 1}, {}, [])

    assert result == {"a": 1}
