import pytest

from hope.apps.periodic_data_update.service.flexible_attribute_service import FlexibleAttributeForPDUService

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    ProgramFactory,
)

pytestmark = pytest.mark.django_db


@pytest.fixture()
def business_area():
    return BusinessAreaFactory()


@pytest.fixture()
def program(business_area):
    return ProgramFactory(business_area=business_area)


@pytest.fixture()
def flex_attr_without_pdu(program):
    return FlexibleAttributeFactory(
        name="field_without_pdu",
        program=program,
        pdu_data=None,
    )


def test_increase_rounds_skips_when_pdu_data_is_none(program, flex_attr_without_pdu):
    pdu_fields = [
        {
            "id": str(flex_attr_without_pdu.id),
            "pdu_data": {"number_of_rounds": 2, "rounds_names": ["Round 1", "Round 2"]},
        }
    ]
    service = FlexibleAttributeForPDUService(program=program, pdu_fields=pdu_fields)

    service.increase_pdu_rounds_for_program_with_rdi()

    flex_attr_without_pdu.refresh_from_db()
    assert flex_attr_without_pdu.pdu_data is None
