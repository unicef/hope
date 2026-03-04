"""Tests for program manager functionality."""

from typing import Any

import pytest

from extras.test_utils.factories import (
    BusinessAreaFactory,
    ProgramFactory,
)
from hope.models import BusinessArea, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def afghanistan(db: Any) -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan")


def test_get_by_unicef_id_returns_program(afghanistan: BusinessArea) -> None:
    program = ProgramFactory(business_area=afghanistan, programme_code="AB12")

    result = Program.objects.get_by_unicef_id(f"{afghanistan.slug}-{program.programme_code.lower()}")

    assert result == program


def test_get_by_unicef_id_not_found(afghanistan: BusinessArea) -> None:
    with pytest.raises(Program.DoesNotExist) as exc_info:
        Program.objects.get_by_unicef_id("missing-id")

    assert str(exc_info.value) == "Program matching unicef_id 'missing-id' does not exist."
