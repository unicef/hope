import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    HouseholdFactory,
    IndividualFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Individual,
    PeriodicFieldData,
    Program,
    RegistrationDataImport,
)


@pytest.fixture
def program(business_area: BusinessArea) -> Program:
    beneficiary_group = BeneficiaryGroupFactory(
        name="Main Menu",
        group_label="Items Group",
        group_label_plural="Items Groups",
        member_label="Item",
        member_label_plural="Items",
        master_detail=True,
    )
    return ProgramFactory(
        name="Test Online Template Program",
        code="OTPL",
        status=Program.ACTIVE,
        business_area=business_area,
        beneficiary_group=beneficiary_group,
    )


@pytest.fixture
def string_attribute(program: Program) -> FlexibleAttribute:
    name = field_label_to_field_name("Test String Attribute")
    flexible_attribute = FlexibleAttribute.objects.create(
        label={"English(EN)": "Test String Attribute"},
        name=name,
        type=FlexibleAttribute.PDU,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    flexible_attribute.pdu_data = PeriodicFieldData.objects.create(
        subtype=FlexibleAttribute.STRING, number_of_rounds=1, rounds_names=["Round 1"]
    )
    flexible_attribute.save()
    return flexible_attribute


@pytest.fixture
def individual(program: Program, business_area: BusinessArea, string_attribute: FlexibleAttribute) -> Individual:
    rdi = RegistrationDataImportFactory(status=RegistrationDataImport.MERGED, program=program)
    hoh = IndividualFactory(
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
    )
    HouseholdFactory(business_area=business_area, program_id=program.pk, registration_data_import=rdi)
    populate_pdu_with_null_values(program, hoh.flex_fields)
    hoh.save()
    return hoh
