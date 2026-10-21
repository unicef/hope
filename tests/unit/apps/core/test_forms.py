import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    BusinessAreaFactory,
    DataCollectingTypeFactory,
    PayeeTypeFactory,
    ProgramFactory,
)
from hope.apps.core.forms import DataCollectingTypeForm, PayeeTypeForm, ProgramForm
from hope.models import BeneficiaryGroup, BusinessArea, DataCollectingType, PayeeType, Program

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


@pytest.fixture
def household_payee_type() -> PayeeType:
    return PayeeTypeFactory(name="Household", gl_code="7700410")


@pytest.fixture
def incentive_payee_type() -> PayeeType:
    return PayeeTypeFactory(name="Incentive Payee", gl_code="7700430")


@pytest.fixture
def household_dct(household_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="full_collection",
        label="Full Collection",
        type=DataCollectingType.Type.STANDARD,
        payee_type=household_payee_type,
    )


@pytest.fixture
def size_only_dct(household_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="size_only",
        label="Size Only",
        type=DataCollectingType.Type.STANDARD,
        payee_type=household_payee_type,
    )


@pytest.fixture
def frontline_dct(incentive_payee_type: PayeeType) -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="frontline_worker_wash",
        label="Frontline Worker Wash",
        type=DataCollectingType.Type.SOCIAL,
        household_filters_available=False,
        payee_type=incentive_payee_type,
    )


@pytest.fixture
def unassigned_social_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="frontline_worker_sp",
        label="Frontline Worker SP",
        type=DataCollectingType.Type.SOCIAL,
        household_filters_available=False,
        payee_type=None,
    )


@pytest.fixture
def unassigned_standard_dct() -> DataCollectingType:
    return DataCollectingTypeFactory(
        code="standalone", label="Standalone", type=DataCollectingType.Type.STANDARD, payee_type=None
    )


@pytest.fixture
def household_with_default_dct(household_payee_type: PayeeType, household_dct: DataCollectingType) -> PayeeType:
    household_payee_type.default_data_collecting_type = household_dct
    household_payee_type.save()
    return household_payee_type


@pytest.fixture
def program_on_size_only(size_only_dct: DataCollectingType) -> Program:
    return ProgramFactory(data_collecting_type=size_only_dct)


@pytest.fixture
def payee_label_restricted_to_size_only(
    household_payee_type: PayeeType, size_only_dct: DataCollectingType
) -> BeneficiaryGroup:
    beneficiary_group = BeneficiaryGroupFactory(name="Size Only Households", payee_type=household_payee_type)
    beneficiary_group.data_collecting_types.add(size_only_dct)
    return beneficiary_group


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
            "payee_type": standard_dct.payee_type_id,
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
        (
            "DCTs of different types cannot be compatible with each other. "
            "Following DCTs are not of type STANDARD: ['Social']"
        )
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
        (
            "DCTs of different types cannot be compatible with each other. "
            "Following DCTs are not of type STANDARD: ['Social']"
        )
    ]


def test_dct_form_allows_editing_collects_individual_data(standard_dct: DataCollectingType) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": standard_dct.code,
            "label": standard_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "collects_individual_data": True,
            "payee_type": standard_dct.payee_type_id,
        },
        instance=standard_dct,
    )

    assert form.is_valid() is True
    assert form.save().collects_individual_data is True


def test_dct_form_requires_payee_type_when_not_deprecated() -> None:
    form = DataCollectingTypeForm(
        data={"code": "new_dct", "label": "New DCT", "type": DataCollectingType.Type.STANDARD, "weight": 1}
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == ["Payee Type is required for a Data Collecting Type that is not deprecated"]


def test_dct_form_allows_missing_payee_type_when_deprecated() -> None:
    form = DataCollectingTypeForm(
        data={
            "code": "unknown",
            "label": "Unknown",
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "deprecated": True,
        }
    )

    assert form.is_valid() is True


def test_dct_form_allows_reassigning_unused_dct_to_another_payee_type(
    household_dct: DataCollectingType, incentive_payee_type: PayeeType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": household_dct.code,
            "label": household_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "payee_type": incentive_payee_type.pk,
        },
        instance=household_dct,
    )

    assert form.is_valid() is True
    assert form.save().payee_type == incentive_payee_type


def test_dct_form_rejects_reassigning_dct_used_by_programs_to_another_payee_type(
    program_on_size_only: Program, size_only_dct: DataCollectingType, incentive_payee_type: PayeeType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": size_only_dct.code,
            "label": size_only_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "payee_type": incentive_payee_type.pk,
        },
        instance=size_only_dct,
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == ["Cannot move or unassign a Data Collecting Type used by programs"]


def test_dct_form_rejects_payee_type_with_data_collecting_types_of_other_type(
    frontline_dct: DataCollectingType, incentive_payee_type: PayeeType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": "new_dct",
            "label": "New DCT",
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "payee_type": incentive_payee_type.pk,
        }
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == ["All Data Collecting Types of a Payee Type must have the same type"]


def test_dct_form_rejects_unassigning_default_dct_of_payee_type(
    household_with_default_dct: PayeeType, household_dct: DataCollectingType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": household_dct.code,
            "label": household_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "deprecated": True,
        },
        instance=household_dct,
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == ["Cannot move or unassign the default Data Collecting Type of its Payee Type"]


def test_dct_form_rejects_unassigning_dct_payee_labels_are_restricted_to(
    payee_label_restricted_to_size_only: BeneficiaryGroup, size_only_dct: DataCollectingType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": size_only_dct.code,
            "label": size_only_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "deprecated": True,
        },
        instance=size_only_dct,
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == [
        "Cannot move or unassign a Data Collecting Type that Payee Labels are restricted to"
    ]


def test_dct_form_rejects_unassigning_dct_used_by_programs(
    program_on_size_only: Program, size_only_dct: DataCollectingType
) -> None:
    form = DataCollectingTypeForm(
        data={
            "code": size_only_dct.code,
            "label": size_only_dct.label,
            "type": DataCollectingType.Type.STANDARD,
            "weight": 1,
            "deprecated": True,
        },
        instance=size_only_dct,
    )

    assert form.is_valid() is False
    assert form.errors["payee_type"] == ["Cannot move or unassign a Data Collecting Type used by programs"]


def test_payee_type_form_initial_lists_assigned_data_collecting_types(
    household_payee_type: PayeeType, household_dct: DataCollectingType
) -> None:
    form = PayeeTypeForm(instance=household_payee_type)

    assert list(form.fields["data_collecting_types"].initial) == [household_dct]


def test_payee_type_form_save_assigns_selected_and_unassigns_removed_dcts(
    incentive_payee_type: PayeeType,
    frontline_dct: DataCollectingType,
    unassigned_social_dct: DataCollectingType,
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Incentive Payee",
            "gl_code": "7700430",
            "weight": 20,
            "active": True,
            "data_collecting_types": [unassigned_social_dct.pk],
            "default_data_collecting_type": unassigned_social_dct.pk,
        },
        instance=incentive_payee_type,
    )

    assert form.is_valid() is True
    form.save()
    unassigned_social_dct.refresh_from_db()
    frontline_dct.refresh_from_db()
    assert unassigned_social_dct.payee_type == incentive_payee_type
    assert frontline_dct.payee_type is None


def test_payee_type_form_rejects_dct_assigned_to_another_payee_type(
    incentive_payee_type: PayeeType, household_dct: DataCollectingType
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Incentive Payee",
            "gl_code": "7700430",
            "weight": 20,
            "data_collecting_types": [household_dct.pk],
        },
        instance=incentive_payee_type,
    )

    assert form.is_valid() is False
    assert form.errors["data_collecting_types"] == [
        "This DCT is already assigned to another Payee Type: Full Collection"
    ]


def test_payee_type_form_rejects_data_collecting_types_of_mixed_type(
    unassigned_social_dct: DataCollectingType, unassigned_standard_dct: DataCollectingType
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Organization",
            "gl_code": "7700430",
            "weight": 10,
            "data_collecting_types": [unassigned_social_dct.pk, unassigned_standard_dct.pk],
        }
    )

    assert form.is_valid() is False
    assert form.errors["data_collecting_types"] == ["All Data Collecting Types of a Payee Type must have the same type"]


def test_payee_type_form_rejects_removing_dct_payee_labels_are_restricted_to(
    household_payee_type: PayeeType,
    payee_label_restricted_to_size_only: BeneficiaryGroup,
    size_only_dct: DataCollectingType,
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Household",
            "gl_code": "7700410",
            "weight": 30,
            "data_collecting_types": [],
        },
        instance=household_payee_type,
    )

    assert form.is_valid() is False
    assert form.errors["data_collecting_types"] == [
        "Cannot remove Data Collecting Types that Payee Labels are restricted to: Size Only"
    ]


def test_payee_type_form_rejects_removing_dct_used_by_programs(
    household_payee_type: PayeeType, program_on_size_only: Program, size_only_dct: DataCollectingType
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Household",
            "gl_code": "7700410",
            "weight": 30,
            "data_collecting_types": [],
        },
        instance=household_payee_type,
    )

    assert form.is_valid() is False
    assert form.errors["data_collecting_types"] == ["Cannot remove Data Collecting Types used by programs: Size Only"]


def test_payee_type_form_rejects_default_dct_outside_selected_dcts(
    household_payee_type: PayeeType, household_dct: DataCollectingType, size_only_dct: DataCollectingType
) -> None:
    form = PayeeTypeForm(
        data={
            "name": "Household",
            "gl_code": "7700410",
            "weight": 30,
            "data_collecting_types": [household_dct.pk],
            "default_data_collecting_type": size_only_dct.pk,
        },
        instance=household_payee_type,
    )

    assert form.is_valid() is False
    assert form.errors["default_data_collecting_type"] == [
        "Default Data Collecting Type must belong to this Payee Type"
    ]


def test_payee_type_form_rejects_active_payee_type_without_default_dct(household_payee_type: PayeeType) -> None:
    form = PayeeTypeForm(
        data={"name": "Household", "gl_code": "7700410", "weight": 30, "active": True},
        instance=household_payee_type,
    )

    assert form.is_valid() is False
    assert form.errors["default_data_collecting_type"] == ["Active Payee Type must have a default Data Collecting Type"]
