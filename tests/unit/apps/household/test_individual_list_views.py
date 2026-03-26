import json
from typing import Any, Callable

from django.core.cache import cache
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AccountFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    DocumentFactory,
    DocumentTypeFactory,
    FlexibleAttributeForPDUFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    PeriodicFieldDataFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.household.const import (
    CANNOT_DO,
    DISABLED,
    DUPLICATE,
    HEARING,
    LOT_DIFFICULTY,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SEEING,
)
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models import (
    AccountType,
    Area,
    BusinessArea,
    DocumentType,
    FlexibleAttribute,
    Household,
    Individual,
    IndividualRoleInHousehold,
    PeriodicFieldData,
    Program,
    User,
)

pytestmark = pytest.mark.django_db


def _generate_delivery_mechanisms() -> None:
    account_types_data = [
        {"payment_gateway_id": "123", "key": "bank", "label": "Bank", "unique_fields": ["number"]},
        {"payment_gateway_id": "456", "key": "mobile", "label": "Mobile", "unique_fields": ["number"]},
    ]
    for at in account_types_data:
        AccountType.objects.update_or_create(
            key=at["key"],
            defaults={
                "label": at["label"],
                "unique_fields": at["unique_fields"],
                "payment_gateway_id": at["payment_gateway_id"],
            },
        )


@pytest.fixture
def afghanistan() -> BusinessArea:
    return BusinessAreaFactory(name="Afghanistan", slug="afghanistan", code="0060")


@pytest.fixture
def program(afghanistan: BusinessArea) -> Program:
    return ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)


@pytest.fixture
def partner() -> Any:
    return PartnerFactory(name="TestPartner")


@pytest.fixture
def user(partner: Any) -> User:
    return UserFactory(partner=partner)


@pytest.fixture
def country() -> Any:
    return CountryFactory()


@pytest.fixture
def areas(country: Any) -> tuple[Area, Area]:
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    return area1, area2


def _create_household(
    program: Program, afghanistan: BusinessArea, area1: Area, area2: Area
) -> tuple[Household, list[Individual]]:
    household = HouseholdFactory(admin1=area1, admin2=area2, program=program, business_area=afghanistan)
    ind1 = IndividualFactory(
        household=household,
        program=program,
        business_area=afghanistan,
        registration_data_import=household.registration_data_import,
    )
    ind2 = IndividualFactory(
        household=household,
        program=program,
        business_area=afghanistan,
        registration_data_import=household.registration_data_import,
    )
    return household, [household.head_of_household, ind1, ind2]


@pytest.fixture
def list_context(
    api_client: Callable, afghanistan: BusinessArea, program: Program, user: User, areas: tuple
) -> dict[str, Any]:
    area1, area2 = areas
    different_program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    list_url = reverse(
        "api:households:individuals-list", kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code}
    )
    count_url = reverse(
        "api:households:individuals-count",
        kwargs={"business_area_slug": afghanistan.slug, "program_code": program.code},
    )
    client = api_client(user)

    household1 = HouseholdFactory(admin1=area1, admin2=area2, program=program, business_area=afghanistan)
    individual1_1 = household1.head_of_household
    individual1_2 = IndividualFactory(
        household=household1,
        program=program,
        business_area=afghanistan,
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(admin1=area1, admin2=area2, program=program, business_area=afghanistan)
    individual2_1 = household2.head_of_household
    individual2_2 = IndividualFactory(
        household=household2,
        program=program,
        business_area=afghanistan,
        registration_data_import=household2.registration_data_import,
    )

    household_dp = HouseholdFactory(admin1=area1, admin2=area2, program=different_program, business_area=afghanistan)
    IndividualFactory(
        household=household_dp,
        program=different_program,
        business_area=afghanistan,
        registration_data_import=household_dp.registration_data_import,
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "different_program": different_program,
        "list_url": list_url,
        "count_url": count_url,
        "client": client,
        "user": user,
        "partner": user.partner,
        "area1": area1,
        "area2": area2,
        "household1": household1,
        "household2": household2,
        "individual1_1": individual1_1,
        "individual1_2": individual1_2,
        "individual2_1": individual2_1,
        "individual2_2": individual2_2,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
    ],
)
def test_individual_list_permissions(
    list_context: dict,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=list_context["user"],
        permissions=permissions,
        business_area=list_context["afghanistan"],
        program=list_context["program"],
    )
    response = list_context["client"].get(list_context["list_url"])
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
    ],
)
def test_individual_count_permissions(
    list_context: dict,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    create_user_role_with_permissions(
        user=list_context["user"],
        permissions=permissions,
        business_area=list_context["afghanistan"],
        program=list_context["program"],
    )
    response = list_context["client"].get(list_context["count_url"])
    assert response.status_code == expected_status


def test_individual_count(list_context: dict, create_user_role_with_permissions: Callable) -> None:
    create_user_role_with_permissions(
        user=list_context["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=list_context["afghanistan"],
        program=list_context["program"],
    )
    response = list_context["client"].get(list_context["count_url"])
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 4


def test_individuals_list(list_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = list_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )

    response = ctx["client"].get(ctx["list_url"])
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    assert len(results) == 4

    response_count = ctx["client"].get(ctx["count_url"])
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 4

    response_ids = [result["id"] for result in results]
    for ind in [ctx["individual1_1"], ctx["individual1_2"], ctx["individual2_1"], ctx["individual2_2"]]:
        assert str(ind.id) in response_ids

    for i, individual in enumerate(
        [ctx["individual1_1"], ctx["individual1_2"], ctx["individual2_1"], ctx["individual2_2"]]
    ):
        individual_result = results[i]
        assert individual_result["id"] == str(individual.id)
        assert individual_result["unicef_id"] == individual.unicef_id
        assert individual_result["full_name"] == individual.full_name
        assert individual_result["status"] == individual.status
        assert individual_result["relationship"] == individual.relationship
        assert individual_result["age"] == individual.age
        assert individual_result["sex"] == individual.sex
        assert individual_result["household"] == {
            "id": str(individual.household.id),
            "unicef_id": individual.household.unicef_id,
            "admin2": {"id": str(individual.household.admin2.id), "name": individual.household.admin2.name},
        }
        assert individual_result["program"] == {
            "id": str(individual.program.id),
            "name": individual.program.name,
            "code": individual.program.code,
        }
        assert individual_result["last_registration_date"] == f"{individual.last_registration_date:%Y-%m-%d}"


def test_individual_list_on_draft_program(list_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = list_context
    draft_program = ProgramFactory(business_area=ctx["afghanistan"], status=Program.DRAFT)
    list_url = reverse(
        "api:households:individuals-list",
        kwargs={"business_area_slug": ctx["afghanistan"].slug, "program_code": draft_program.code},
    )
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=ctx["afghanistan"],
        program=draft_program,
    )
    HouseholdFactory(program=draft_program, business_area=ctx["afghanistan"])

    response = ctx["client"].get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_individual_list_with_admin_area_limits(
    list_context: dict,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    ctx = list_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    set_admin_area_limits_in_program(ctx["partner"], ctx["program"], [ctx["area1"]])

    household_no_area = HouseholdFactory(program=ctx["program"], business_area=ctx["afghanistan"])
    individual_no_area1 = household_no_area.head_of_household
    individual_no_area2 = IndividualFactory(
        household=household_no_area,
        program=ctx["program"],
        business_area=ctx["afghanistan"],
        registration_data_import=household_no_area.registration_data_import,
    )

    area_different = AreaFactory(parent=None, p_code="AF05", area_type=ctx["area1"].area_type)
    household_different_areas = HouseholdFactory(
        admin1=ctx["area1"], admin2=ctx["area2"], program=ctx["program"], business_area=ctx["afghanistan"]
    )
    individual_different_areas1 = household_different_areas.head_of_household
    individual_different_areas2 = IndividualFactory(
        household=household_different_areas,
        program=ctx["program"],
        business_area=ctx["afghanistan"],
        registration_data_import=household_different_areas.registration_data_import,
    )
    household_different_areas.admin1 = area_different
    household_different_areas.admin2 = area_different
    household_different_areas.save()

    response = ctx["client"].get(ctx["list_url"])
    assert response.status_code == status.HTTP_200_OK
    response_ids = [r["id"] for r in response.data["results"]]
    assert len(response_ids) == 6
    for ind in [
        ctx["individual1_1"],
        ctx["individual1_2"],
        ctx["individual2_1"],
        ctx["individual2_2"],
        individual_no_area1,
        individual_no_area2,
    ]:
        assert str(ind.id) in response_ids
    for ind in [individual_different_areas1, individual_different_areas2]:
        assert str(ind.id) not in response_ids


def test_individual_list_caching(
    list_context: dict,
    create_user_role_with_permissions: Callable,
    set_admin_area_limits_in_program: Callable,
) -> None:
    ctx = list_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )

    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 4
        assert len(captured.captured_queries) == 20

    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second = response.headers["etag"]
        assert etag_second == etag
        assert len(captured.captured_queries) == 8

    ctx["individual1_1"].given_name = "Jane"
    ctx["individual1_1"].save()
    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        etag_third = response.headers["etag"]
        assert json.loads(cache.get(etag_third)[0].decode("utf8")) == response.json()
        assert etag_third not in [etag, etag_second]
        assert len(captured.captured_queries) == 15

    set_admin_area_limits_in_program(ctx["partner"], ctx["program"], [ctx["area1"]])
    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        etag_changed_areas = response.headers["etag"]
        assert json.loads(cache.get(etag_changed_areas)[0].decode("utf8")) == response.json()
        assert etag_changed_areas not in [etag, etag_second, etag_third]
        assert len(captured.captured_queries) == 15

    ctx["individual1_2"].delete()
    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        etag_fourth = response.headers["etag"]
        assert len(response.json()["results"]) == 3
        assert etag_fourth not in [etag, etag_second, etag_third, etag_changed_areas]
        assert len(captured.captured_queries) == 15

    with CaptureQueriesContext(connection) as captured:
        response = ctx["client"].get(ctx["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["etag"] == etag_fourth
        assert len(captured.captured_queries) == 8


def test_individual_list_deduplication_result_serializer(
    list_context: dict, create_user_role_with_permissions: Callable
) -> None:
    from datetime import date

    from dateutil.relativedelta import relativedelta

    ctx = list_context
    dob = "1981-03-11"
    hh = HouseholdFactory(program=ctx["program"], business_area=ctx["afghanistan"])
    duplicate_individual = IndividualFactory(
        household=hh,
        program=ctx["program"],
        business_area=ctx["afghanistan"],
        full_name="das asd asd",
        birth_date=date(1981, 3, 11),
        registration_data_import=hh.registration_data_import,
    )

    ctx["individual1_1"].deduplication_golden_record_status = DUPLICATE
    ctx["individual1_1"].deduplication_golden_record_results = {
        "duplicates": [
            {
                "dob": dob,
                "score": 25.0,
                "hit_id": str(duplicate_individual.id),
                "location": None,
                "full_name": duplicate_individual.full_name,
                "proximity_to_score": 14.0,
            }
        ],
        "possible_duplicates": [],
    }
    ctx["individual1_1"].save()

    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(ctx["list_url"])
    assert response.status_code == status.HTTP_200_OK
    results = response.json()["results"]
    ind = next(r for r in results if r["id"] == str(ctx["individual1_1"].id))
    assert "deduplication_golden_record_results" in ind
    assert ind["deduplication_golden_record_results"][0]["hit_id"] == str(duplicate_individual.id)
    assert ind["deduplication_golden_record_results"][0]["full_name"] == "das asd asd"
    assert ind["deduplication_golden_record_results"][0]["age"] == relativedelta(date.today(), date(1981, 3, 11)).years
    assert ind["deduplication_golden_record_results"][0]["score"] == 25.0
    assert ind["deduplication_golden_record_results"][0]["proximity_to_score"] == 14.0
    assert ind["deduplication_golden_record_results"][0]["location"] is None


def test_individual_all_flex_fields_attributes(list_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = list_context
    draft_program = ProgramFactory(business_area=ctx["afghanistan"], status=Program.DRAFT)
    list_url = reverse(
        "api:households:individuals-all-flex-fields-attributes",
        kwargs={"business_area_slug": ctx["afghanistan"].slug, "program_code": draft_program.code},
    )
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
        business_area=ctx["afghanistan"],
        program=draft_program,
    )
    FlexibleAttribute.objects.create(
        name="Flexible Attribute for INDIVIDUAL",
        type=FlexibleAttribute.STRING,
        label={"English(EN)": "Test Flex", "Test": ""},
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=draft_program,
    )
    response = ctx["client"].get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Flexible Attribute for INDIVIDUAL"


@pytest.fixture
def detail_context(
    api_client: Callable, afghanistan: BusinessArea, program: Program, user: User, country: Any
) -> dict[str, Any]:
    client = api_client(user)

    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_2)
    area4 = AreaFactory(parent=area3, p_code="AF01010101", area_type=admin_type_2)

    registration_data_import = RegistrationDataImportFactory(
        imported_by=user, business_area=afghanistan, program=program
    )

    household = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        admin3=area3,
        admin4=area4,
        country=country,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        registration_data_import=registration_data_import,
        start=timezone.now(),
    )
    individual1 = household.head_of_household
    individual1.pregnant = True
    individual1.observed_disability = [SEEING, HEARING]
    individual1.seeing_disability = LOT_DIFFICULTY
    individual1.hearing_disability = CANNOT_DO
    individual1.disability = DISABLED
    individual1.photo = ContentFile(b"abc", name="1.png")
    individual1.deduplication_golden_record_status = DUPLICATE
    individual1.duplicate = True
    individual1.save()

    individual2 = IndividualFactory(
        household=household,
        program=program,
        business_area=afghanistan,
        registration_data_import=registration_data_import,
    )

    household2 = HouseholdFactory(
        program=program, business_area=afghanistan, start=timezone.now(), country=country, country_origin=country
    )

    role_alternate = IndividualRoleInHouseholdFactory(individual=individual1, household=household2, role=ROLE_ALTERNATE)
    role_primary = IndividualRoleInHousehold.objects.get(individual=individual1, household=household, role=ROLE_PRIMARY)

    grievance_ticket = GrievanceTicketFactory(household_unicef_id=household.unicef_id)
    GrievanceTicketFactory()

    image_flex_attr = FlexibleAttribute.objects.create(
        label={"English(EN)": "profile_image_i_f"},
        name="profile_image_i_f",
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
        program=program,
    )
    pdu_data1 = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.DECIMAL, number_of_rounds=3, rounds_names=["Round 1", "Round 2", "Round 3"]
    )
    FlexibleAttributeForPDUFactory(program=program, label="PDU Field 1", pdu_data=pdu_data1)
    pdu_data2 = PeriodicFieldDataFactory(
        subtype=PeriodicFieldData.STRING, number_of_rounds=4, rounds_names=["Round A", "Round B", "Round C", "Round D"]
    )
    FlexibleAttributeForPDUFactory(program=program, label="PDU Field 2", pdu_data=pdu_data2)

    individual1.flex_fields = {
        "wellbeing_index_i_f": 24,
        "school_enrolled_before_i_f": 1,
        "profile_image_i_f": "profile_image_i_f.png",
    }
    individual1.flex_fields = populate_pdu_with_null_values(program, individual1.flex_fields)
    individual1.flex_fields["pdu_field_1"]["1"] = {"value": 123.45, "collection_date": "2021-01-01"}
    individual1.flex_fields["pdu_field_1"]["2"] = {"value": 234.56, "collection_date": "2021-01-01"}
    individual1.flex_fields["pdu_field_2"]["4"] = {"value": "Value D", "collection_date": "2021-01-01"}
    individual1.save()

    national_id_type = DocumentTypeFactory(key="national_id")
    national_passport_type = DocumentTypeFactory(key="national_passport")
    tax_id_type = DocumentTypeFactory(key="tax_id")
    birth_certificate_type = DocumentTypeFactory(key="birth_certificate")
    disability_card_type = DocumentTypeFactory(key="disability_card")
    drivers_license_type = DocumentTypeFactory(key="drivers_license")

    national_id = DocumentFactory(
        document_number="123-456-789",
        type=DocumentType.objects.get(key="national_id"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc.png"),
    )
    national_passport = DocumentFactory(
        document_number="111-222-333",
        type=DocumentTypeFactory(key="national_passport"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc2.png"),
    )
    birth_certificate = DocumentFactory(
        document_number="111222333",
        type=DocumentType.objects.get(key="birth_certificate"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc3.png"),
    )
    disability_card = DocumentFactory(
        document_number="10000000000",
        type=DocumentType.objects.get(key="disability_card"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc4.png"),
    )
    drivers_license = DocumentFactory(
        document_number="1234567890",
        type=DocumentType.objects.get(key="drivers_license"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc5.png"),
    )
    tax_id = DocumentFactory(
        document_number="666-777-888",
        type=DocumentType.objects.get(key="tax_id"),
        individual=individual1,
        program=program,
        country=country,
        photo=ContentFile(b"abc", name="doc6.png"),
    )

    identity = IndividualIdentityFactory(country=country, individual=individual1)

    _generate_delivery_mechanisms()
    AccountFactory(
        individual=individual1,
        data={"card_number__bank": "123", "card_expiry_date__bank": "2022-01-01", "name_of_cardholder__bank": "Marek"},
    )
    AccountFactory(
        individual=individual1,
        data={
            "service_provider_code__mobile": "ABC",
            "delivery_phone_number__mobile": "123456789",
            "provider__mobile": "Provider",
        },
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "user": user,
        "client": client,
        "registration_data_import": registration_data_import,
        "household": household,
        "household2": household2,
        "individual1": individual1,
        "individual2": individual2,
        "role_primary": role_primary,
        "role_alternate": role_alternate,
        "grievance_ticket": grievance_ticket,
        "country": country,
        "national_id": national_id,
        "national_passport": national_passport,
        "birth_certificate": birth_certificate,
        "disability_card": disability_card,
        "drivers_license": drivers_license,
        "tax_id": tax_id,
        "national_id_type": national_id_type,
        "national_passport_type": national_passport_type,
        "tax_id_type": tax_id_type,
        "birth_certificate_type": birth_certificate_type,
        "disability_card_type": disability_card_type,
        "drivers_license_type": drivers_license_type,
        "identity": identity,
        "image_flex_attr": image_flex_attr,
    }


@pytest.mark.parametrize(
    ("permissions", "expected_status"),
    [
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], status.HTTP_200_OK),
        ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
        ([], status.HTTP_403_FORBIDDEN),
        ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_403_FORBIDDEN),
    ],
)
def test_individual_detail_permissions(
    detail_context: dict,
    permissions: list,
    expected_status: int,
    create_user_role_with_permissions: Callable,
) -> None:
    ctx = detail_context
    create_user_role_with_permissions(
        user=ctx["user"], permissions=permissions, business_area=ctx["afghanistan"], program=ctx["program"]
    )
    response = ctx["client"].get(
        reverse(
            "api:households:individuals-detail",
            kwargs={
                "business_area_slug": ctx["afghanistan"].slug,
                "program_code": ctx["program"].code,
                "pk": str(ctx["individual1"].id),
            },
        )
    )
    assert response.status_code == expected_status


def test_individual_detail(detail_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = detail_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[
            Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
        ],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(
        reverse(
            "api:households:individuals-detail",
            kwargs={
                "business_area_slug": ctx["afghanistan"].slug,
                "program_code": ctx["program"].code,
                "pk": str(ctx["individual1"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    ind1 = ctx["individual1"]
    hh = ctx["household"]
    hh2 = ctx["household2"]
    rdi = ctx["registration_data_import"]
    country = ctx["country"]

    assert data["id"] == str(ind1.id)
    assert data["unicef_id"] == ind1.unicef_id
    assert data["full_name"] == ind1.full_name
    assert data["given_name"] == ind1.given_name
    assert data["middle_name"] == ind1.middle_name
    assert data["family_name"] == ind1.family_name
    assert data["sex"] == ind1.sex
    assert data["age"] == ind1.age
    assert data["birth_date"] == f"{ind1.birth_date:%Y-%m-%d}"
    assert data["estimated_birth_date"] == ind1.estimated_birth_date
    assert data["marital_status"] == ind1.marital_status
    assert data["work_status"] == ind1.work_status
    assert data["pregnant"] == ind1.pregnant
    assert data["household"] == {
        "id": str(hh.id),
        "unicef_id": hh.unicef_id,
        "admin1": {"id": str(hh.admin1.id), "name": hh.admin1.name},
        "admin2": {"id": str(hh.admin2.id), "name": hh.admin2.name},
        "admin3": {"id": str(hh.admin3.id), "name": hh.admin3.name},
        "admin4": {"id": str(hh.admin4.id), "name": hh.admin4.name},
        "first_registration_date": f"{hh.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
        "last_registration_date": f"{hh.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
        "total_cash_received": None,
        "total_cash_received_usd": None,
        "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
        "start": hh.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "zip_code": None,
        "residence_status": hh.get_residence_status_display(),
        "country_origin": hh.country_origin.name,
        "country": hh.country.name,
        "address": hh.address,
        "village": hh.village,
        "geopoint": None,
        "import_id": hh.unicef_id,
        "program_code": ctx["program"].code,
    }
    assert data["role"] == ROLE_PRIMARY
    assert data["relationship"] == ind1.relationship
    assert data["registration_data_import"] == {
        "id": str(rdi.id),
        "name": rdi.name,
        "status": rdi.status,
        "import_date": f"{rdi.import_date:%Y-%m-%dT%H:%M:%SZ}",
        "number_of_individuals": rdi.number_of_individuals,
        "number_of_households": rdi.number_of_households,
        "imported_by": {
            "id": str(rdi.imported_by.id),
            "first_name": rdi.imported_by.first_name,
            "last_name": rdi.imported_by.last_name,
            "email": rdi.imported_by.email,
            "username": rdi.imported_by.username,
        },
        "data_source": rdi.data_source,
    }
    assert data["import_id"] == ind1.unicef_id
    assert data["admin_url"] is None
    assert data["preferred_language"] == ind1.preferred_language
    assert data["roles_in_households"] == [
        {
            "id": str(ctx["role_primary"].id),
            "household": {
                "id": str(hh.id),
                "unicef_id": hh.unicef_id,
                "admin1": {"id": str(hh.admin1.id), "name": hh.admin1.name},
                "admin2": {"id": str(hh.admin2.id), "name": hh.admin2.name},
                "admin3": {"id": str(hh.admin3.id), "name": hh.admin3.name},
                "admin4": {"id": str(hh.admin4.id), "name": hh.admin4.name},
                "first_registration_date": f"{hh.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{hh.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": hh.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": hh.get_residence_status_display(),
                "country_origin": hh.country_origin.name,
                "country": hh.country.name,
                "address": hh.address,
                "village": hh.village,
                "geopoint": None,
                "import_id": hh.unicef_id,
                "program_code": ctx["program"].code,
            },
            "role": ROLE_PRIMARY,
        },
        {
            "id": str(ctx["role_alternate"].id),
            "household": {
                "id": str(hh2.id),
                "unicef_id": hh2.unicef_id,
                "admin1": None,
                "admin2": None,
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{hh2.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{hh2.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": hh2.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": hh2.get_residence_status_display(),
                "country_origin": hh2.country_origin.name,
                "country": hh2.country.name,
                "address": hh2.address,
                "village": hh2.village,
                "geopoint": None,
                "import_id": hh2.unicef_id,
                "program_code": ctx["program"].code,
            },
            "role": ROLE_ALTERNATE,
        },
    ]
    assert data["observed_disability"] == ind1.observed_disability
    assert data["seeing_disability"] == ind1.seeing_disability
    assert data["hearing_disability"] == ind1.hearing_disability
    assert data["physical_disability"] == ind1.physical_disability
    assert data["memory_disability"] == ind1.memory_disability
    assert data["selfcare_disability"] == ind1.selfcare_disability
    assert data["comms_disability"] == ind1.comms_disability
    assert data["disability"] == ind1.disability
    assert data["email"] == ind1.email
    assert data["phone_no"] == ind1.phone_no
    assert data["phone_no_alternative"] == ind1.phone_no_alternative
    assert data["sanction_list_last_check"] == ind1.sanction_list_last_check
    assert data["wallet_name"] == ind1.wallet_name
    assert data["blockchain_name"] == ind1.blockchain_name
    assert data["wallet_address"] == ind1.wallet_address
    assert data["status"] == ind1.status
    assert data["flex_fields"] == {
        "wellbeing_index_i_f": 24,
        "school_enrolled_before_i_f": 1,
        "profile_image_i_f": default_storage.url("profile_image_i_f.png"),
        "pdu_field_1": {
            "1": {"collection_date": "2021-01-01", "value": 123.45},
            "2": {"collection_date": "2021-01-01", "value": 234.56},
        },
        "pdu_field_2": {"4": {"collection_date": "2021-01-01", "value": "Value D"}},
    }

    expected_docs = [
        {
            "id": str(ctx["national_id"].id),
            "type": {
                "id": str(ctx["national_id_type"].id),
                "label": ctx["national_id_type"].label,
                "key": ctx["national_id_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["national_id"].document_number,
            "photo": ctx["national_id"].photo.url,
        },
        {
            "id": str(ctx["national_passport"].id),
            "type": {
                "id": str(ctx["national_passport_type"].id),
                "label": ctx["national_passport_type"].label,
                "key": ctx["national_passport_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["national_passport"].document_number,
            "photo": ctx["national_passport"].photo.url,
        },
        {
            "id": str(ctx["birth_certificate"].id),
            "type": {
                "id": str(ctx["birth_certificate_type"].id),
                "label": ctx["birth_certificate_type"].label,
                "key": ctx["birth_certificate_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["birth_certificate"].document_number,
            "photo": ctx["birth_certificate"].photo.url,
        },
        {
            "id": str(ctx["disability_card"].id),
            "type": {
                "id": str(ctx["disability_card_type"].id),
                "label": ctx["disability_card_type"].label,
                "key": ctx["disability_card_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["disability_card"].document_number,
            "photo": ctx["disability_card"].photo.url,
        },
        {
            "id": str(ctx["drivers_license"].id),
            "type": {
                "id": str(ctx["drivers_license_type"].id),
                "label": ctx["drivers_license_type"].label,
                "key": ctx["drivers_license_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["drivers_license"].document_number,
            "photo": ctx["drivers_license"].photo.url,
        },
        {
            "id": str(ctx["tax_id"].id),
            "type": {
                "id": str(ctx["tax_id_type"].id),
                "label": ctx["tax_id_type"].label,
                "key": ctx["tax_id_type"].key,
            },
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "document_number": ctx["tax_id"].document_number,
            "photo": ctx["tax_id"].photo.url,
        },
    ]
    assert sorted(data["documents"], key=lambda x: x["id"]) == sorted(expected_docs, key=lambda x: x["id"])
    assert data["identities"] == [
        {
            "id": ctx["identity"].id,
            "country": {"id": str(country.id), "name": country.name, "iso_code3": country.iso_code3},
            "partner": None,
            "number": ctx["identity"].number,
        }
    ]
    assert len(data["accounts"]) == 2
    assert data["accounts"][1]["data_fields"] == [
        {"key": "card_expiry_date__bank", "value": "2022-01-01"},
        {"key": "card_number__bank", "value": "123"},
        {"key": "name_of_cardholder__bank", "value": "Marek"},
    ]
    assert data["accounts"][0]["data_fields"] == [
        {"key": "delivery_phone_number__mobile", "value": "123456789"},
        {"key": "provider__mobile", "value": "Provider"},
        {"key": "service_provider_code__mobile", "value": "ABC"},
    ]
    assert data["linked_grievances"] == [
        {
            "id": str(ctx["grievance_ticket"].id),
            "unicef_id": str(ctx["grievance_ticket"].unicef_id),
            "category": ctx["grievance_ticket"].category,
            "status": ctx["grievance_ticket"].status,
        }
    ]
    assert data["enrolled_in_nutrition_programme"] == ind1.enrolled_in_nutrition_programme
    assert data["who_answers_phone"] == ind1.who_answers_phone
    assert data["who_answers_alt_phone"] == ind1.who_answers_alt_phone
    assert data["payment_delivery_phone_no"] == ind1.payment_delivery_phone_no


def test_individual_detail_admin_url(detail_context: dict) -> None:
    ctx = detail_context
    ctx["user"].is_superuser = True
    ctx["user"].save()
    response = ctx["client"].get(
        reverse(
            "api:households:individuals-detail",
            kwargs={
                "business_area_slug": ctx["afghanistan"].slug,
                "program_code": ctx["program"].code,
                "pk": str(ctx["individual1"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == ctx["individual1"].admin_url


def test_get_individual_photos(detail_context: dict, create_user_role_with_permissions: Callable) -> None:
    ctx = detail_context
    create_user_role_with_permissions(
        user=ctx["user"],
        permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
        business_area=ctx["afghanistan"],
        program=ctx["program"],
    )
    response = ctx["client"].get(
        reverse(
            "api:households:individuals-photos",
            kwargs={
                "business_area_slug": ctx["afghanistan"].slug,
                "program_code": ctx["program"].code,
                "pk": str(ctx["individual1"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == str(ctx["individual1"].id)
    assert data["photo"] is not None
    assert data["documents"][0]["document_number"] == "666-777-888"
    assert data["documents"][0]["photo"] is not None
