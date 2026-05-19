from io import BytesIO
import re
from typing import Any
from unittest.mock import MagicMock, patch

from constance.test import override_config
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
    FlexibleAttributeChoiceFactory,
    FlexibleAttributeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
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
    handle_add_identity,
    handle_edit_document,
    handle_edit_identity,
    handle_photo,
    handle_role,
    prepare_previous_documents,
    prepare_previous_identities,
    save_images,
    to_phone_number_str,
    update_es,
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
from hope.apps.registration_data.api.deduplication_engine import IgnoredFilenamesPair
from hope.models import (
    DeduplicationEngineSimilarityPair,
    Document,
    FlexibleAttribute,
    IndividualRoleInHousehold,
)
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
@patch("hope.apps.registration_data.api.deduplication_engine.DeduplicationEngineAPI.report_false_positive_duplicate")
def test_close_needs_adjudication_ticket_service_for_biometrics(
    dedup_engine_api_report_false_positive_duplicate_mock: MagicMock,
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
    dedup_engine_api_report_false_positive_duplicate_mock.assert_not_called()

    ticket_details.selected_distinct.set([individual_1, individual_2])
    ticket_details.selected_individuals.set([])
    ticket_details.save()
    close_needs_adjudication_ticket_service(ticket, user)
    dedup_engine_api_report_false_positive_duplicate_mock.assert_called_once_with(
        IgnoredFilenamesPair(first=f"{individual_1.photo.name}", second=f"{individual_2.photo.name}"),
        program.unicef_id,
    )


@patch.dict(
    "os.environ",
    {
        "DEDUPLICATION_ENGINE_API_KEY": "dedup_api_key",
        "DEDUPLICATION_ENGINE_API_URL": "http://dedup-fake-url.com",
    },
)
@patch("hope.apps.grievance.services.needs_adjudication_ticket_services.logger")
@patch("hope.apps.registration_data.services.biometric_deduplication.BiometricDeduplicationService")
def test_close_needs_adjudication_ticket_service_for_biometrics_when_deduplication_engine_fails(
    biometric_dedup_service_mock: MagicMock,
    mock_logger: Any,
    user: Any,
    business_area: Any,
    program: Any,
) -> None:
    rdi = RegistrationDataImportFactory(program=program, business_area=business_area)
    household = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual = household.head_of_household
    individual.photo = ContentFile(b"abc", name="ind1.png")
    individual.save(update_fields=["photo"])
    household_2 = HouseholdFactory(program=program, business_area=business_area, create_role=False)
    individual_2 = household_2.head_of_household
    individual_2.photo = ContentFile(b"aaa", name="ind2.png")
    individual_2.save(update_fields=["photo"])

    grievance = GrievanceTicketFactory(
        category=GrievanceTicket.CATEGORY_NEEDS_ADJUDICATION,
        issue_type=GrievanceTicket.ISSUE_TYPE_BIOMETRICS_SIMILARITY,
        business_area=business_area,
        status=GrievanceTicket.STATUS_FOR_APPROVAL,
        description="GrievanceTicket",
        registration_data_import=rdi,
    )
    grievance.programs.add(program)
    ticket_details = TicketNeedsAdjudicationDetailsFactory(
        ticket=grievance,
        golden_records_individual=individual,
        is_multiple_duplicates_version=True,
        selected_individual=None,
    )
    ticket_details.selected_distinct.add(individual)

    mock_service = biometric_dedup_service_mock.return_value

    class FakeAPIError(Exception):
        pass

    mock_service.api.API_EXCEPTION_CLASS = FakeAPIError
    mock_service.report_false_positive_duplicate.side_effect = FakeAPIError()

    # check with one Individual
    # skip report false positive duplicate to Deduplication Engine
    close_needs_adjudication_ticket_service(grievance, user)
    mock_service.report_false_positive_duplicate.assert_not_called()

    # process with two Inds
    ticket_details.selected_distinct.add(individual_2)
    close_needs_adjudication_ticket_service(grievance, user)

    mock_service.report_false_positive_duplicate.assert_called_once()
    mock_logger.exception.assert_called_once_with("Failed to report false positive duplicate to Deduplication Engine")


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


def test_verify_flex_fields_invalid_type() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.STRING,
        name="string_field_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )

    with pytest.raises(ValueError, match="invalid value type for a field string_field_i_f"):
        verify_flex_fields({"string_field_i_f": 123}, "individuals")


def test_verify_flex_fields_select_one_invalid_value() -> None:
    attr = FlexibleAttributeFactory(
        type=FlexibleAttribute.SELECT_ONE,
        name="select_one_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    attr.choices.add(FlexibleAttributeChoiceFactory(name="OPTION_A"))

    with pytest.raises(ValueError, match="invalid value: OPTION_X for a field select_one_i_f"):
        verify_flex_fields({"select_one_i_f": "OPTION_X"}, "individuals")


def test_verify_flex_fields_select_many_valid_value() -> None:
    attr = FlexibleAttributeFactory(
        type=FlexibleAttribute.SELECT_MANY,
        name="select_many_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    attr.choices.add(FlexibleAttributeChoiceFactory(name="A"))
    attr.choices.add(FlexibleAttributeChoiceFactory(name="B"))

    verify_flex_fields({"select_many_i_f": ["A", "B"]}, "individuals")


def test_verify_flex_fields_select_many_invalid_value() -> None:
    attr = FlexibleAttributeFactory(
        type=FlexibleAttribute.SELECT_MANY,
        name="select_many_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    attr.choices.add(FlexibleAttributeChoiceFactory(name="A"))

    with pytest.raises(ValueError, match=r"invalid value: \['A', 'X'\] for a field select_many_i_f"):
        verify_flex_fields({"select_many_i_f": ["A", "X"]}, "individuals")


def test_handle_edit_document_without_photo_keeps_existing(program: Any) -> None:
    country = CountryFactory(
        name="Austria",
        short_name="Austria",
        iso_code2="AT",
        iso_code3="AUT",
        iso_num="040",
    )
    document_type = DocumentTypeFactory(key="NO_PHOTO_DOC", label="no photo doc")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    document = DocumentFactory(
        individual=individual,
        document_number="OLD-NUM",
        type=document_type,
        country=country,
        program=program,
        status=Document.STATUS_VALID,
    )
    document_data = {
        "id": str(document.id),
        "key": "NO_PHOTO_DOC",
        "country": "AUT",
        "number": "NEW-NUM",
        "photo": None,
        "photoraw": None,
    }

    result = handle_edit_document(document_data)

    assert result.document_number == "NEW-NUM"
    assert not result.photo


def test_handle_edit_document_swaps_photo_with_photoraw(program: Any) -> None:
    country = CountryFactory(
        name="Belgium",
        short_name="Belgium",
        iso_code2="BE",
        iso_code3="BEL",
        iso_num="056",
    )
    document_type = DocumentTypeFactory(key="EDIT_DOC", label="edit doc")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    document = DocumentFactory(
        individual=individual,
        document_number="OLD-NUM",
        type=document_type,
        country=country,
        program=program,
        status=Document.STATUS_VALID,
    )
    document_data = {
        "id": str(document.id),
        "key": "EDIT_DOC",
        "country": "BEL",
        "number": "NEW-NUM",
        "photo": "https://cdn.example/photo.jpg",
        "photoraw": "raw-name.jpg",
    }

    result = handle_edit_document(document_data)

    assert result.id == document.id
    assert result.document_number == "NEW-NUM"
    assert result.country.iso_code3 == "BEL"


def test_handle_add_identity_duplicate_raises(program: Any) -> None:
    country = CountryFactory(
        name="Chile",
        short_name="Chile",
        iso_code2="CL",
        iso_code3="CHL",
        iso_num="152",
    )
    partner = PartnerFactory(name="UNHCR")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    IndividualIdentityFactory(individual=individual, partner=partner, country=country, number="ID-1")

    identity_data = {"partner": "UNHCR", "country": "CHL", "number": "ID-1"}

    with pytest.raises(DRFValidationError) as error:
        handle_add_identity(identity_data, individual)
    assert "Identity with number ID-1, partner: UNHCR already exists" in str(error.value)


def test_handle_edit_identity_updates_fields(program: Any) -> None:
    country = CountryFactory(
        name="Denmark",
        short_name="Denmark",
        iso_code2="DK",
        iso_code3="DNK",
        iso_num="208",
    )
    old_partner = PartnerFactory(name="OLD_PARTNER")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    identity = IndividualIdentityFactory(
        individual=individual,
        partner=old_partner,
        country=country,
        number="OLD-NUM",
    )

    identity_data = {
        "value": {
            "id": str(identity.id),
            "partner": "NEW_PARTNER",
            "number": "NEW-NUM",
            "country": "DNK",
        }
    }

    result = handle_edit_identity(identity_data)

    assert result.id == identity.id
    assert result.number == "NEW-NUM"
    assert result.partner.name == "NEW_PARTNER"
    assert result.country.iso_code3 == "DNK"


def test_handle_edit_identity_duplicate_raises(program: Any) -> None:
    country = CountryFactory(
        name="Egypt",
        short_name="Egypt",
        iso_code2="EG",
        iso_code3="EGY",
        iso_num="818",
    )
    partner = PartnerFactory(name="DUP_PARTNER")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    target = IndividualIdentityFactory(individual=individual, partner=partner, country=country, number="UNIQUE")
    IndividualIdentityFactory(individual=individual, partner=partner, country=country, number="TAKEN")

    identity_data = {
        "value": {
            "id": str(target.id),
            "partner": "DUP_PARTNER",
            "number": "TAKEN",
            "country": "EGY",
        }
    }

    with pytest.raises(DRFValidationError) as error:
        handle_edit_identity(identity_data)
    assert "Identity with number TAKEN, partner: DUP_PARTNER already exists" in str(error.value)


def test_prepare_previous_documents(program: Any) -> None:
    country = CountryFactory(
        name="France",
        short_name="France",
        iso_code2="FR",
        iso_code3="FRA",
        iso_num="250",
    )
    document_type = DocumentTypeFactory(key="PREV_DOC", label="prev doc")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    document = DocumentFactory(
        individual=individual,
        document_number="PREV-1",
        type=document_type,
        country=country,
        program=program,
    )

    result = prepare_previous_documents([{"value": str(document.id)}])

    assert result == {
        str(document.id): {
            "id": str(document.id),
            "document_number": "PREV-1",
            "individual": str(individual.id),
            "key": "PREV_DOC",
            "country": "FRA",
        }
    }


def test_prepare_previous_identities(program: Any) -> None:
    country = CountryFactory(
        name="Greece",
        short_name="Greece",
        iso_code2="GR",
        iso_code3="GRC",
        iso_num="300",
    )
    partner = PartnerFactory(name="PREV_PARTNER")
    individual = IndividualFactory(program=program, business_area=program.business_area)
    identity = IndividualIdentityFactory(individual=individual, partner=partner, country=country, number="PREV-ID")

    result = prepare_previous_identities([{"value": str(identity.id)}])

    assert result == {
        str(identity.id): {
            "id": str(identity.id),
            "number": "PREV-ID",
            "individual": str(individual.id),
            "partner": "PREV_PARTNER",
            "country": "GRC",
        }
    }


def test_save_images_invalid_associated_with() -> None:
    with pytest.raises(
        ValueError,
        match=re.escape("associated_with argument must be one of ['household', 'individual']"),
    ):
        save_images({"any_field": "any_value"}, "wrong_target")


def test_save_images_unknown_flex_field_raises() -> None:
    with pytest.raises(ValueError, match="unknown_field is not a correct `flex field"):
        save_images({"unknown_field": "value"}, "individuals")


def test_save_images_persists_uploaded_image() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.IMAGE,
        name="profile_picture_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    uploaded = InMemoryUploadedFile(
        file=BytesIO(b"img-bytes"),
        field_name="profile_picture_i_f",
        name="pic.jpg",
        content_type="image/jpeg",
        size=9,
        charset=None,
    )
    flex_fields: dict[str, Any] = {"profile_picture_i_f": uploaded}

    save_images(flex_fields, "individuals")

    assert isinstance(flex_fields["profile_picture_i_f"], str)
    assert flex_fields["profile_picture_i_f"].endswith(".jpg")


def test_save_images_unquotes_url_string() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.IMAGE,
        name="profile_picture_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    flex_fields = {"profile_picture_i_f": "/api/uploads/some%20encoded.jpg"}

    save_images(flex_fields, "individuals")

    assert "%20" not in flex_fields["profile_picture_i_f"]
    assert "some encoded.jpg" in flex_fields["profile_picture_i_f"]


def test_save_images_skips_non_image_fields() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.STRING,
        name="non_image_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    flex_fields = {"non_image_i_f": "untouched"}

    save_images(flex_fields, "individuals")

    assert flex_fields == {"non_image_i_f": "untouched"}


def test_save_images_image_field_with_unsupported_value_type() -> None:
    FlexibleAttributeFactory(
        type=FlexibleAttribute.IMAGE,
        name="picture_i_f",
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
    )
    flex_fields: dict[str, Any] = {"picture_i_f": None}

    save_images(flex_fields, "individuals")

    assert flex_fields == {"picture_i_f": None}


@override_config(IS_ELASTICSEARCH_ENABLED=False)
def test_update_es_returns_early_when_disabled(program: Any, mocker: Any) -> None:
    individual = IndividualFactory(program=program, business_area=program.business_area)
    mock_individual_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_individual_doc")
    mock_household_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_household_doc")

    update_es(individual)

    mock_individual_doc.assert_not_called()
    mock_household_doc.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_update_es_indexes_individual_without_household(program: Any, mocker: Any) -> None:
    individual = IndividualFactory(program=program, business_area=program.business_area)
    mock_individual_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_individual_doc")
    mock_household_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_household_doc")

    update_es(individual)

    mock_individual_doc.assert_called_once_with(str(individual.program.id))
    mock_individual_doc.return_value.return_value.update.assert_called_once_with(individual)
    mock_household_doc.assert_not_called()


@override_config(IS_ELASTICSEARCH_ENABLED=True)
def test_update_es_indexes_individual_and_household(program: Any, mocker: Any) -> None:
    household = HouseholdFactory(program=program, business_area=program.business_area, create_role=False)
    individual = household.head_of_household
    mock_individual_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_individual_doc")
    mock_household_doc = mocker.patch("hope.apps.grievance.services.data_change.utils.get_household_doc")

    update_es(individual)

    mock_individual_doc.assert_called_once_with(str(individual.program.id))
    mock_household_doc.assert_called_once_with(str(individual.program.id))
    mock_household_doc.return_value.return_value.update.assert_called_once_with(individual.household)
