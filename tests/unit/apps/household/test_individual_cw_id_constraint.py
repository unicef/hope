from django.db import IntegrityError, transaction
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory
from extras.test_utils.factories.household import IndividualFactory
from extras.test_utils.factories.program import ProgramFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def cw_business_area():
    return BusinessAreaFactory(name="CW Area", slug="cw-area")


@pytest.fixture
def cw_program(cw_business_area):
    return ProgramFactory(business_area=cw_business_area)


def test_duplicate_country_workspace_id_in_same_business_area_is_rejected(cw_business_area, cw_program) -> None:
    IndividualFactory(
        business_area=cw_business_area,
        program=cw_program,
        country_workspace_id="CW-1",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        IndividualFactory(
            business_area=cw_business_area,
            program=cw_program,
            country_workspace_id="CW-1",
        )


def test_same_country_workspace_id_in_another_business_area_is_allowed(cw_business_area, cw_program) -> None:
    other_business_area = BusinessAreaFactory(name="Other Area", slug="other-area")
    other_program = ProgramFactory(business_area=other_business_area)
    IndividualFactory(
        business_area=cw_business_area,
        program=cw_program,
        country_workspace_id="CW-2",
    )

    individual = IndividualFactory(
        business_area=other_business_area,
        program=other_program,
        country_workspace_id="CW-2",
    )

    assert individual.country_workspace_id == "CW-2"


def test_country_workspace_id_of_withdrawn_individual_can_be_reused(cw_business_area, cw_program) -> None:
    IndividualFactory(
        business_area=cw_business_area,
        program=cw_program,
        country_workspace_id="CW-3",
        withdrawn=True,
    )

    individual = IndividualFactory(
        business_area=cw_business_area,
        program=cw_program,
        country_workspace_id="CW-3",
    )

    assert individual.country_workspace_id == "CW-3"


def test_multiple_individuals_without_country_workspace_id_are_allowed(cw_business_area, cw_program) -> None:
    IndividualFactory(business_area=cw_business_area, program=cw_program, country_workspace_id=None)

    individual = IndividualFactory(
        business_area=cw_business_area,
        program=cw_program,
        country_workspace_id=None,
    )

    assert individual.country_workspace_id is None
