from datetime import date
from typing import Any

from django.core.exceptions import ValidationError
from django.forms import IntegerField
from freezegun import freeze_time
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.core.filters import IntegerFilter, filter_age
from hope.models import Individual, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def program() -> Program:
    return ProgramFactory(business_area=BusinessAreaFactory(slug="afghanistan"))


@pytest.fixture
def individual_age_5(program: Program) -> Individual:
    return IndividualFactory(
        household=None,
        program=program,
        business_area=program.business_area,
        birth_date=date(2020, 1, 1),
    )


@pytest.fixture
def individual_age_20(program: Program) -> Individual:
    return IndividualFactory(
        household=None,
        program=program,
        business_area=program.business_area,
        birth_date=date(2005, 1, 1),
    )


@pytest.fixture
def individual_age_40(program: Program) -> Individual:
    return IndividualFactory(
        household=None,
        program=program,
        business_area=program.business_area,
        birth_date=date(1985, 1, 1),
    )


@freeze_time("2025-01-01")
def test_filter_age_with_min_and_max_returns_only_individuals_in_range(
    individual_age_5: Individual,
    individual_age_20: Individual,
    individual_age_40: Individual,
    django_assert_num_queries: Any,
) -> None:
    filtered = filter_age("birth_date", Individual.objects.all(), min_age=18, max_age=30)

    with django_assert_num_queries(1):
        results = set(filtered)

    assert results == {individual_age_20}


@freeze_time("2025-01-01")
def test_filter_age_with_only_min_returns_individuals_at_least_that_old(
    individual_age_5: Individual,
    individual_age_20: Individual,
    individual_age_40: Individual,
    django_assert_num_queries: Any,
) -> None:
    filtered = filter_age("birth_date", Individual.objects.all(), min_age=18, max_age=None)

    with django_assert_num_queries(1):
        results = set(filtered)

    assert results == {individual_age_20, individual_age_40}


@freeze_time("2025-01-01")
def test_filter_age_with_only_max_returns_individuals_younger_than_that(
    individual_age_5: Individual,
    individual_age_20: Individual,
    individual_age_40: Individual,
    django_assert_num_queries: Any,
) -> None:
    filtered = filter_age("birth_date", Individual.objects.all(), min_age=None, max_age=18)

    with django_assert_num_queries(1):
        results = set(filtered)

    assert results == {individual_age_5}


def test_filter_age_without_min_and_max_returns_queryset_unchanged(
    individual_age_20: Individual,
) -> None:
    qs = Individual.objects.all()

    filtered = filter_age("birth_date", qs, min_age=None, max_age=None)

    assert filtered is qs


def test_integer_filter_field_parses_decimal_string_with_zero_fraction_to_int() -> None:
    integer_filter = IntegerFilter()

    assert integer_filter.field_class is IntegerField
    assert integer_filter.field.clean("12.00") == 12


def test_integer_filter_field_rejects_fractional_value() -> None:
    integer_filter = IntegerFilter()

    with pytest.raises(ValidationError, match="Enter a whole number."):
        integer_filter.field.clean("12.04")
