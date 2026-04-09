"""Unit tests for ``extras.test_utils.queries.assert_db_queries_num``.

These tests decorate locally-defined inner functions rather than real pytest
test functions, so that we can exercise both the success and failure paths of
the decorator directly without contorting pytest's own reporting.
"""

from __future__ import annotations

import pytest

from extras.test_utils.queries import assert_db_queries_num
from hope.models.currency import Currency


def test_exact_match_passes(currency_pln: Currency) -> None:
    @assert_db_queries_num(1)
    def inner() -> None:
        Currency.objects.filter(code="PLN").exists()

    inner()


def test_mismatch_raises_with_expected_message_shape(currency_pln: Currency) -> None:
    @assert_db_queries_num(99)
    def inner() -> None:
        Currency.objects.filter(code="PLN").exists()

    with pytest.raises(AssertionError) as exc_info:
        inner()

    message = str(exc_info.value)
    assert "expected 99 queries, got 1 (-98)" in message
    assert "If this change is intentional, update the decorator value." in message
    assert "inner" in message  # qualname of the wrapped function


@pytest.mark.parametrize("code", ["PLN"])
def test_parametrize_shared_n(code: str, currency_pln: Currency) -> None:
    @assert_db_queries_num(1)
    def inner() -> None:
        Currency.objects.filter(code=code).exists()

    inner()


def test_bare_string_using_is_rejected() -> None:
    with pytest.raises(TypeError, match="must be a list/tuple"):
        assert_db_queries_num(1, using="default")  # type: ignore[arg-type]


def test_explicit_default_alias_matches_implicit(currency_pln: Currency) -> None:
    @assert_db_queries_num(1, using=["default"])
    def inner() -> None:
        Currency.objects.filter(code="PLN").exists()

    inner()


@pytest.mark.django_db(databases=["default", "read_only"])
def test_multi_alias_sum(currency_pln: Currency) -> None:
    @assert_db_queries_num(2, using=["default", "read_only"])
    def inner() -> None:
        Currency.objects.using("default").filter(code="PLN").exists()
        Currency.objects.using("read_only").filter(code="PLN").exists()

    inner()


def test_empty_using_is_rejected() -> None:
    with pytest.raises(TypeError, match="at least one alias"):
        assert_db_queries_num(1, using=[])


def test_non_int_n_is_rejected() -> None:
    with pytest.raises(TypeError, match="`n` must be an int"):
        assert_db_queries_num("1")  # type: ignore[arg-type]


def test_async_function_is_rejected() -> None:
    async def async_test() -> None:
        pass

    with pytest.raises(NotImplementedError, match="does not yet support async"):
        assert_db_queries_num(1)(async_test)


def test_exception_propagates_without_count_assertion(currency_pln: Currency) -> None:
    @assert_db_queries_num(99)
    def inner() -> None:
        Currency.objects.filter(code="PLN").exists()
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        inner()
