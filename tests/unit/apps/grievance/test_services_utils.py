from io import BytesIO
import re
from typing import Any
from unittest.mock import MagicMock, patch

from django.core.exceptions import PermissionDenied
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories import (
    AdminAreaLimitedToFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DeduplicationEngineSimilarityPairFactory,
    DocumentFactory,
    DocumentTypeFactory,
    FlexibleAttributeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    TicketNeedsAdjudicationDetailsFactory,
    UserFactory,
)
from hope.apps.grievance.api.mixins import GrievanceMutationMixin
from hope.apps.grievance.models import GrievanceTicket
from hope.apps.grievance.services.data_change.utils import (
    cast_flex_fields,
    convert_to_empty_string_if_null,
    handle_add_document,
    handle_photo,
    handle_role,
    to_phone_number_str,
    verify_flex_fields,
)
from hope.apps.grievance.services.needs_adjudication_ticket_services import (
    close_needs_adjudication_ticket_service,
    create_grievance_ticket_with_details,
)
from hope.apps.grievance.utils import (
    validate_all_individuals_before_close_needs_adjudication,
    validate_individual_for_need_adjudication,
)
from hope.apps.household.const import ROLE_ALTERNATE, ROLE_PRIMARY
from hope.models import DeduplicationEngineSimilarityPair, Document, FlexibleAttribute, IndividualRoleInHousehold
from hope.models.utils import MergeStatusModel

pytestmark = [
    pytest.mark.usefixtures("mock_elasticsearch"),
    pytest.mark.django_db,
]


@pytest.fixture
def business_area() -> Any:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def program(business_area: Any) -> Any:
    return ProgramFactory(business_area=business_area)


@pytest.fixture
def user() -> Any:
    return UserFactory()


@pytest.fixture
def adjudication_areas() -> dict[str, Any]:
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="004",
    )
    area_type_level_1 = AreaTypeFactory(name="Province", area_level=1, country=country)
    area_type_level_2 = AreaTypeFactory(name="District", area_level=2, parent=area_type_level_1, country=country)
    ghazni = AreaFactory(name="Ghazni", area_type=area_type_level_1, p_code="area1")
    doshi = AreaFactory(name="Doshi", area_type=area_type_level_2, p_code="area2", parent=ghazni)
    area_other = AreaFactory(name="Other", area_type=area_type_level_2, p_code="area3")
    return {"doshi": doshi, "area_other": area_other}


def test_convert_to_empty_string_if_null() -> None:
    assert convert_to_empty_string_if_null(None) == ""
    assert convert_to_empty_string_if_null(True)
    assert not convert_to_empty_string_if_null(False)
    assert convert_to_empty_string_if_null("test") == "test"
    assert convert_to_empty_string_if_null(123) == 123


def test_to_phone_number_str() -> None:
    data = {"phone_number": 123456789}
    to_phone_number_str(data, "phone_number")
    assert data["phone_number"] == "123456789"

    data = {"phone_number": 123456789}
    to_phone_number_str(data, "other_field_name")
    assert data["phone_number"] == 123456789


@patch("hope.models.flexible_attribute.FlexibleAttribute.objects.filter")
def test_cast_flex_fields(mock_filter: Any) -> None:
    mock_filter.side_effect = [
        MagicMock(values_list=MagicMock(return_value=["decimal_field"])),
        MagicMock(values_list=MagicMock(return_value=["integer_field"])),
    ]

    flex_fields = {
        "decimal_field": "321.11",
        "integer_field": "123",
        "string_field": "some_string",
    }
    cast_flex_fields(flex_fields)

    assert flex_fields["string_field"] == "some_string"
    assert flex_fields["integer_field"] == 123
    assert flex_fields["decimal_field"] == 321.11


def test_verify_flex_fields() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("associated_with argument must be one of ['household', 'individual']"),
    ):
        verify_flex_fields({"key": "value"}, "associated_with")

    with pytest.raises(ValueError, match="key is not a correct `flex field"):
        verify_flex_fields({"key": "value"}, "individuals")


def test_verify_flex_fields_with_date_type() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.DATE,
        name="national_id_issue_date_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "value123"},
    )

    verify_flex_fields({"national_id_issue_date_i_f": "2025-01-15"}, "individuals")

    with pytest.raises(ValueError, match="time data 'invalid' does not match format '%Y-%m-%d'"):
        verify_flex_fields({"national_id_issue_date_i_f": "invalid"}, "individuals")


def test_verify_flex_fields_with_int() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.INTEGER,
        name="test_int_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        label={"English(EN)": "int123"},
    )

    verify_flex_fields({"test_int_i_f": "1233"}, "individuals")
    verify_flex_fields({"test_int_i_f": 1233}, "individuals")


def test_handle_role(program: Any) -> None:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual = household.head_of_household

    assert IndividualRoleInHousehold.objects.count() == 0
    IndividualRoleInHouseholdFactory(household=household, individual=individual, role=ROLE_PRIMARY)
    with pytest.raises(DRFValidationError) as error:
        handle_role(household, individual, ROLE_ALTERNATE)
    assert "Ticket cannot be closed, primary collector role has to be reassigned" in str(error.value)

    IndividualRoleInHousehold.objects.filter(household=household).update(role=ROLE_ALTERNATE)
    handle_role(household, individual, None)
    assert IndividualRoleInHousehold.objects.filter(household=household).count() == 0

    handle_role(household, individual, ROLE_ALTERNATE)
    role = IndividualRoleInHousehold.objects.get(household=household, individual=individual)
    assert role.role == ROLE_ALTERNATE
    assert role.rdi_merge_status == MergeStatusModel.MERGED


def test_handle_add_document(program: Any) -> None:
    country = CountryFactory(
        name="Afghanistan",
        short_name="Afghanistan",
        iso_code2="AF",
        iso_code3="AFG",
        iso_num="004",
    )
    document_type = DocumentTypeFactory(key="TAX", label="tax")
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual = household.head_of_household
    document_data = {
        "key": "TAX",
        "country": "AFG",
        "number": "111",
        "photo": "photo",
        "photoraw": "photo_raw",
    }
    DocumentFactory(
        individual=individual,
        document_number="111",
        type=document_type,
        country=country,
        program=program,
        status=Document.STATUS_VALID,
    )

    with pytest.raises(DRFValidationError) as error:
        handle_add_document(document_data, individual)
    assert "Document with number 111 of type tax already exists" in str(error.value)

    document_type.unique_for_individual = True
    document_type.save(update_fields=["unique_for_individual"])
    with pytest.raises(DRFValidationError) as error:
        handle_add_document(document_data, individual)
    assert "Document with number 111 of type tax already exists" in str(error.value)

    Document.objects.all().delete()
    assert Document.objects.count() == 0

    document = handle_add_document(document_data, individual)
    assert isinstance(document, Document)
    assert document.rdi_merge_status == MergeStatusModel.MERGED


def test_validate_individual_for_need_adjudication(
    business_area: Any,
    program: Any,
    adjudication_areas: dict[str, Any],
) -> None:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
    )
    grievance.programs.add(program)

    household_1 = HouseholdFactory(
        business_area=business_area,
        program=program,
        admin2=adjudication_areas["doshi"],
        create_role=False,
    )
    individual_1 = household_1.head_of_household

    household_2 = HouseholdFactory(
        business_area=business_area,
        program=program,
        admin2=adjudication_areas["doshi"],
        create_role=False,
    )
    individual_2 = household_2.head_of_household

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=individual_1,
        possible_duplicate=individual_2,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )

    partner_other = PartnerFactory(name="other")
    AdminAreaLimitedToFactory(
        partner=partner_other,
        program=program,
        areas=[adjudication_areas["area_other"]],
    )
    partner_unicef = PartnerFactory()

    with pytest.raises(PermissionDenied) as error:
        validate_individual_for_need_adjudication(partner_other, individual_1, ticket_details)
    assert str(error.value) == "Permission Denied: User does not have access to select individual"

    outsider_household = HouseholdFactory(
        business_area=business_area,
        program=program,
        admin2=adjudication_areas["doshi"],
        create_role=False,
    )
    outsider_individual = outsider_household.head_of_household

    with pytest.raises(DRFValidationError) as error:
        validate_individual_for_need_adjudication(partner_unicef, outsider_individual, ticket_details)
    assert (
        f"The selected individual {outsider_individual.unicef_id} "
        f"is not valid, must be one of those attached to the ticket" in str(error.value)
    )

    ticket_details.possible_duplicates.add(outsider_individual)
    outsider_individual.withdraw()
    with pytest.raises(DRFValidationError) as error:
        validate_individual_for_need_adjudication(partner_unicef, outsider_individual, ticket_details)
    assert (
        error.value.args[0]
        == f"The selected individual {outsider_individual.unicef_id} is not valid, must be not withdrawn"
    )

    outsider_individual.unwithdraw()
    validate_individual_for_need_adjudication(partner_unicef, outsider_individual, ticket_details)

    ticket_details.selected_distinct.remove(outsider_individual)
    outsider_individual.unwithdraw()
    validate_individual_for_need_adjudication(partner_unicef, outsider_individual, ticket_details)


def test_validate_all_individuals_before_close_needs_adjudication(program: Any) -> None:
    household_1 = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual_1 = household_1.head_of_household

    household_2 = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual_2 = household_2.head_of_household

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        golden_records_individual=individual_1,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.possible_duplicates.add(individual_2)

    with pytest.raises(DRFValidationError) as error:
        validate_all_individuals_before_close_needs_adjudication(ticket_details)
    assert (
        error.value.args[0]
        == "Close ticket is possible when at least one individual is flagged as distinct or one of the individuals is "
        "withdrawn or duplicate"
    )

    ticket_details.selected_distinct.add(individual_2)
    with pytest.raises(DRFValidationError) as error:
        validate_all_individuals_before_close_needs_adjudication(ticket_details)
    assert error.value.args[0] == "Close ticket is possible when all active Individuals are flagged"

    ticket_details.selected_individuals.add(individual_1)
    validate_all_individuals_before_close_needs_adjudication(ticket_details)


def test_close_needs_adjudication_ticket_service(user: Any, business_area: Any, program: Any) -> None:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
    )
    grievance.programs.add(program)

    household_1 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_1 = household_1.head_of_household
    IndividualFactory(
        household=household_1,
        program=program,
        business_area=business_area,
        registration_data_import=household_1.registration_data_import,
    )

    household_2 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_2 = household_2.head_of_household

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=individual_1,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.selected_individuals.add(individual_2)
    ticket_details.possible_duplicates.add(individual_2)
    ticket_details.selected_distinct.add(individual_1)

    close_needs_adjudication_ticket_service(grievance, user)

    individual_1.refresh_from_db()
    individual_2.refresh_from_db()
    assert individual_1.duplicate is False
    assert individual_2.duplicate is True


def test_close_needs_adjudication_ticket_service_individual_without_household(
    user: Any,
    business_area: Any,
    program: Any,
) -> None:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
    )
    grievance.programs.add(program)

    individual_1 = IndividualFactory(household=None, program=program, business_area=business_area)
    document = DocumentFactory(individual=individual_1, status=Document.STATUS_INVALID, program=program)

    household_2 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_2 = household_2.head_of_household

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=individual_1,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.selected_distinct.set([individual_1, individual_2])

    close_needs_adjudication_ticket_service(grievance, user)

    individual_1.refresh_from_db()
    individual_2.refresh_from_db()
    document.refresh_from_db()
    assert individual_1.duplicate is False
    assert individual_2.duplicate is False
    assert document.status == Document.STATUS_VALID


def test_close_needs_adjudication_ticket_service_when_just_duplicates(
    user: Any,
    business_area: Any,
    program: Any,
) -> None:
    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
    )
    grievance.programs.add(program)

    household_1 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_1 = household_1.head_of_household
    IndividualFactory(
        household=household_1,
        program=program,
        business_area=business_area,
        registration_data_import=household_1.registration_data_import,
    )

    household_2 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_2 = household_2.head_of_household

    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=individual_1,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.selected_individuals.add(individual_1)
    ticket_details.possible_duplicates.add(individual_2)

    individual_2.withdraw()
    with pytest.raises(DRFValidationError) as error:
        close_needs_adjudication_ticket_service(grievance, user)
    assert error.value.args[0] == "Close ticket is not possible when all Individuals are flagged as duplicates"

    grievance_2 = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_UNIQUE_IDENTIFIERS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
    )
    grievance_2.programs.add(program)
    ticket_details_2 = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance_2,
        golden_records_individual=individual_1,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details_2.selected_individuals.add(individual_2)
    ticket_details_2.possible_duplicates.add(individual_2)

    with pytest.raises(DRFValidationError) as error:
        close_needs_adjudication_ticket_service(grievance_2, user)
    assert (
        error.value.args[0]
        == "Close ticket is possible when at least one individual is flagged as distinct or one of the individuals is "
        "withdrawn or duplicate"
    )


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch(
    "hope.apps.registration_data.services"
    ".biometric_deduplication"
    ".BiometricDeduplicationService"
    ".report_false_positive_duplicate"
)
def test_close_needs_adjudication_ticket_service_for_biometrics(
    report_false_positive_duplicate_mock: MagicMock,
    user: Any,
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(program=program, business_area=business_area)
    household_1 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    household_2 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_1 = household_1.head_of_household
    individual_2 = household_2.head_of_household
    individual_1.photo = ContentFile(b"...", name="1.png")
    individual_2.photo = ContentFile(b"...", name="2.png")
    individual_1.save(update_fields=["photo"])
    individual_2.save(update_fields=["photo"])

    ticket, ticket_details = create_grievance_ticket_with_details(
        main_individual=individual_1,
        possible_duplicate=individual_2,
        business_area=business_area,
        registration_data_import=household_1.registration_data_import,
        possible_duplicates=[individual_2],
        is_multiple_duplicates_version=True,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
        dedup_engine_similarity_pair=DeduplicationEngineSimilarityPairFactory(
            program=program,
            individual1=individual_1,
            individual2=individual_2,
            similarity_score=90.55,
            status_code=DeduplicationEngineSimilarityPair.StatusCode.STATUS_200,
        ),
    )
    assert ticket is not None
    assert ticket_details is not None

    ticket.registration_data_import = rdi
    ticket.save(update_fields=["registration_data_import"])

    ticket_details.selected_distinct.set([individual_1])
    ticket_details.selected_individuals.set([individual_2])
    close_needs_adjudication_ticket_service(ticket, user)
    report_false_positive_duplicate_mock.assert_not_called()

    ticket_details.selected_distinct.set([individual_1, individual_2])
    ticket_details.selected_individuals.set([])
    close_needs_adjudication_ticket_service(ticket, user)
    report_false_positive_duplicate_mock.assert_called_once_with(
        str(individual_1.photo.name),
        str(individual_2.photo.name),
        str(program.unicef_id),
    )


def test_create_grievance_ticket_with_details_no_possible_duplicates(business_area: Any, program: Any) -> None:
    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    main_individual = household.head_of_household

    ticket, ticket_details = create_grievance_ticket_with_details(
        main_individual=main_individual,
        possible_duplicate=None,
        business_area=business_area,
        registration_data_import=household.registration_data_import,
        possible_duplicates=[],
        is_multiple_duplicates_version=True,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOGRAPHICAL_DATA_SIMILARITY,
    )
    assert ticket is None
    assert ticket_details is None


def test_handle_photo_string_returns_photoraw() -> None:
    result = handle_photo(
        photo="already-exists",
        photoraw="https://cdn.example.com/photo.jpg",
    )
    assert result == "https://cdn.example.com/photo.jpg"


def test_handle_photo_saves_and_return() -> None:
    file = InMemoryUploadedFile(
        file=BytesIO(b"123"),
        field_name="photo",
        name="test123.jpg",
        content_type="image/jpeg",
        size=3,
        charset=None,
    )
    result = handle_photo(file, photoraw=None)
    assert result is not None
    assert result.endswith(".jpg")


def test_set_status_based_on_assigned_to(user: Any) -> None:
    mixin = GrievanceMutationMixin()
    grievance_ticket_1 = GrievanceTicketFactory(
        created_by=user,
        status=GrievanceTicket.STATUS_NEW,
        assigned_to=None,
    )
    grievance_ticket_2 = GrievanceTicketFactory(
        created_by=user,
        status=GrievanceTicket.STATUS_ON_HOLD,
        assigned_to=user,
    )

    mixin._set_status_based_on_assigned_to(approver=user, grievance_ticket=grievance_ticket_1, messages=[])
    mixin._set_status_based_on_assigned_to(approver=user, grievance_ticket=grievance_ticket_2, messages=[])

    assert grievance_ticket_1.status == GrievanceTicket.STATUS_ASSIGNED
    assert grievance_ticket_2.status == GrievanceTicket.STATUS_IN_PROGRESS
