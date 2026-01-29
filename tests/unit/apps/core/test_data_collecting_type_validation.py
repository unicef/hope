from django.core.exceptions import ValidationError
import pytest

from extras.test_utils.factories.core import BusinessAreaFactory, DataCollectingTypeFactory
from hope.models import DataCollectingType


@pytest.fixture
def business_area(db):
    return BusinessAreaFactory()


@pytest.fixture
def dct_full(business_area):
    dct = DataCollectingTypeFactory(label="Full", code="full")
    dct.limit_to.add(business_area)
    return dct


@pytest.fixture
def dct_partial(business_area):
    dct = DataCollectingTypeFactory(label="Partial", code="partial")
    dct.limit_to.add(business_area)
    return dct


@pytest.fixture
def dct_social(business_area):
    dct = DataCollectingTypeFactory(
        label="SocialDCT",
        code="socialdct",
        type=DataCollectingType.Type.SOCIAL,
    )
    dct.limit_to.add(business_area)
    return dct


def test_dct_change_type_succeeds_when_no_compatible_dcts(dct_full):
    dct_full.type = DataCollectingType.Type.SOCIAL

    dct_full.save()

    dct_full.refresh_from_db()
    assert dct_full.type == DataCollectingType.Type.SOCIAL


def test_dct_change_type_raises_when_compatible_dct_has_different_type(dct_full, dct_partial):
    dct_full.compatible_types.add(dct_partial)
    dct_full.type = DataCollectingType.Type.SOCIAL

    with pytest.raises(ValidationError) as error:
        dct_full.save()

    assert str(error.value.messages[0]) == "Type of DCT cannot be changed if it has compatible DCTs of different type."


def test_dct_add_compatible_type_raises_when_different_type(dct_full, dct_social):
    with pytest.raises(ValidationError) as error:
        dct_full.compatible_types.add(dct_social)

    assert str(error.value.messages[0]) == "DCTs of different types cannot be compatible with each other."
