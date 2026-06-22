import pytest

from extras.test_utils.factories import BusinessAreaFactory, DataCollectingTypeFactory, ProgramFactory
from hope.apps.core.forms import DataCollectingTypeForm, ProgramForm
from hope.models import BusinessArea, DataCollectingType, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def active_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.ACTIVE)


@pytest.fixture
def draft_program(business_area: BusinessArea) -> Program:
    return ProgramFactory(business_area=business_area, status=Program.DRAFT)


@pytest.fixture
def other_business_area_program() -> Program:
    return ProgramFactory(business_area=BusinessAreaFactory(slug="ukraine"), status=Program.ACTIVE)


@pytest.fixture
def standard_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(code="full", label="Full", type=DataCollectingType.Type.STANDARD)


@pytest.fixture
def social_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(code="social", label="Social", type=DataCollectingType.Type.SOCIAL)


def test_program_form_lists_only_active_programs_from_business_area(
    business_area: BusinessArea,
    active_program: Program,
    draft_program: Program,
    other_business_area_program: Program,
) -> None:
    form = ProgramForm(business_area_id=business_area.id)

    assert list(form.get_program_queryset()) == [active_program]


def test_program_form_valid_with_active_program(business_area: BusinessArea, active_program: Program) -> None:
    form = ProgramForm(data={"name": "New RDI", "program": active_program.pk}, business_area_id=business_area.id)

    assert form.is_valid() is True
    assert form.cleaned_data["program"] == active_program


def test_program_form_rejects_program_from_another_business_area(
    business_area: BusinessArea, other_business_area_program: Program
) -> None:
    form = ProgramForm(
        data={"name": "New RDI", "program": other_business_area_program.pk},
        business_area_id=business_area.id,
    )

    assert form.is_valid() is False
    assert "program" in form.errors


def test_dct_form_valid_with_compatible_types_of_same_type(standard_dct: DataCollectingType) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": "new_dct",
            "label": "New DCT",
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "compatible_types": [standard_dct.pk],
        }
    )

    assert form.is_valid() is True
    assert form.instance.skip_type_validation is True


def test_dct_form_requires_type() -> None:
    form = DataCollectingTypeForm(data={"code": "new_dct", "label": "New DCT", "weight": 1})

    assert form.is_valid() is False
    assert form.errors["type"] == ["This field is required."]


def test_dct_form_rejects_household_filters_for_social_type() -> None:
    form = DataCollectingTypeForm(
        data={
            "code": "new_dct",
            "label": "New DCT",
            "type": DataCollectingType.Type.SOCIAL,
            "weight": 1,
            "household_filters_available": True,
        }
    )

    assert form.is_valid() is False
    assert form.errors["type"] == ["Household filters cannot be applied for data collecting type with social type"]


def test_dct_form_rejects_type_change_and_incompatible_compatible_types(
    social_dct: DataCollectingType,
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": "new_dct",
            "label": "New DCT",
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "compatible_types": [social_dct.pk],
        }
    )

    assert form.is_valid() is False
    assert form.errors["type"] == ["Type of DCT cannot be changed if it has compatible DCTs of different type"]
    assert form.errors["compatible_types"] == [
        "DCTs of different types cannot be compatible with each other. "
        "Following DCTs are not of type STANDARD: ['Social']"
    ]


def test_dct_form_keeps_type_error_out_when_type_is_unchanged(
    standard_dct: DataCollectingType, social_dct: DataCollectingType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": standard_dct.code,
            "label": standard_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "compatible_types": [social_dct.pk],
        },
        instance=standard_dct,
    )

    assert form.is_valid() is False
    assert "type" not in form.errors
    assert form.errors["compatible_types"] == [
        "DCTs of different types cannot be compatible with each other. "
        "Following DCTs are not of type STANDARD: ['Social']"
    ]
