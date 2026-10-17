from collections.abc import Callable

import pytest

from extras.test_utils.factories import (
    BeneficiaryGroupFactory,
    HouseholdFactory,
    IndividualFactory,
    PDUOnlineEditFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
)
from hope.apps.periodic_data_update.service.periodic_data_update_online_edit_generate_data_service import (
    PDUOnlineEditGenerateDataService,
)
from hope.apps.periodic_data_update.utils import (
    field_label_to_field_name,
    populate_pdu_with_null_values,
)
from hope.models import (
    BusinessArea,
    FlexibleAttribute,
    Individual,
    PDUOnlineEdit,
    PeriodicFieldData,
    Program,
    RegistrationDataImport,
    User,
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
        unicef_id="IND-00-0000.0001",
        household=None,
        business_area=business_area,
        program=program,
        registration_data_import=rdi,
    )
    HouseholdFactory(business_area=business_area, program_id=program.pk, registration_data_import=rdi)
    populate_pdu_with_null_values(program, hoh.flex_fields)
    hoh.save()
    hoh.refresh_from_db()
    return hoh


@pytest.fixture
def online_edit_factory(
    program: Program,
    string_attribute: FlexibleAttribute,
    individual: Individual,
    create_super_user: User,
) -> Callable[..., PDUOnlineEdit]:
    """Build an online edit for `individual` with the same edit_data the create wizard generates."""

    def make(
        status: str = PDUOnlineEdit.Status.NEW,
        value: str | None = None,
        authorized_users: list[User] | None = None,
    ) -> PDUOnlineEdit:
        rounds_data = [{"field": string_attribute.name, "round": 1, "round_name": "Round 1"}]
        edit_data = PDUOnlineEditGenerateDataService(program, {}, rounds_data).generate_edit_data()
        if value is not None:
            field = edit_data[0]["pdu_fields"][string_attribute.name]
            field["value"] = value
            field["collection_date"] = "2026-01-15"
        return PDUOnlineEditFactory(
            program=program,
            business_area=program.business_area,
            created_by=create_super_user,
            status=status,
            edit_data=edit_data,
            number_of_records=len(edit_data),
            authorized_users=[create_super_user] if authorized_users is None else authorized_users,
        )

    return make
