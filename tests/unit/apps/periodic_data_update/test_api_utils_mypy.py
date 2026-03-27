import pytest
from rest_framework import serializers

from hope.apps.periodic_data_update.api.utils import add_round_names_to_rounds_data

from extras.test_utils.factories import (
    BusinessAreaFactory,
    FlexibleAttributeFactory,
    PeriodicFieldDataFactory,
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
def flex_attr_with_pdu(program):
    pdu_data = PeriodicFieldDataFactory(subtype="STRING", number_of_rounds=1, rounds_names=["Round 1"])
    return FlexibleAttributeFactory(
        name="test_pdu_field",
        program=program,
        pdu_data=pdu_data,
    )


def test_add_round_names_raises_when_round_is_none(program, flex_attr_with_pdu):
    rounds_data = [{"field": flex_attr_with_pdu.name, "round": None}]

    with pytest.raises(serializers.ValidationError, match="Round number is required"):
        add_round_names_to_rounds_data(rounds_data, program)
