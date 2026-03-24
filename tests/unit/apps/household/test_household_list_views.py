import json
from typing import Any

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories import (
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CommunicationMessageFactory,
    CountryFactory,
    FlexibleAttributeFactory,
    GrievanceTicketFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualRoleInHouseholdFactory,
    PartnerFactory,
    PaymentFactory,
    PaymentPlanFactory,
    ProgramCycleFactory,
    ProgramFactory,
    RegistrationDataImportFactory,
    SurveyFactory,
    UserFactory,
)
from hope.apps.account.permissions import Permissions
from hope.apps.core.utils import resolve_flex_fields_choices_to_string
from hope.apps.household.const import DUPLICATE, ROLE_PRIMARY
from hope.models import FlexibleAttribute, Payment, Program

pytestmark = pytest.mark.django_db


@pytest.fixture
def household_list_context(api_client: Any) -> dict[str, Any]:
    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    different_program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)

    list_url = reverse(
        "api:households:households-list",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )
    count_url = reverse(
        "api:households:households-count",
        kwargs={
            "business_area_slug": afghanistan.slug,
            "program_slug": program.slug,
        },
    )

    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)

    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)

    household1 = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        size=2,
    )
    IndividualFactory(
        household=household1,
        business_area=afghanistan,
        program=program,
        registration_data_import=household1.registration_data_import,
    )

    household2 = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country_origin=country,
        program=program,
        business_area=afghanistan,
        size=2,
    )
    IndividualFactory(
        household=household2,
        business_area=afghanistan,
        program=program,
        registration_data_import=household2.registration_data_import,
    )

    household_from_different_program = HouseholdFactory(
        admin1=area1,
        admin2=area2,
        country_origin=country,
        program=different_program,
        business_area=afghanistan,
        size=2,
    )
    IndividualFactory(
        household=household_from_different_program,
        business_area=afghanistan,
        program=different_program,
        registration_data_import=household_from_different_program.registration_data_import,
    )

    return {
        "afghanistan": afghanistan,
        "program": program,
        "different_program": different_program,
        "list_url": list_url,
        "count_url": count_url,
        "partner": partner,
        "user": user,
        "api_client": client,
        "country": country,
        "area1": area1,
        "area2": area2,
        "household1": household1,
        "household2": household2,
        "household_from_different_program": household_from_different_program,
    }


@pytest.mark.parametrize(
    "permissions",
    [
        (Permissions.RDI_VIEW_DETAILS,),
        (Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST,),
    ],
)
def test_household_list_with_permissions(
    permissions: list,
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=permissions,
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )

    response = household_list_context["api_client"].get(household_list_context["list_url"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.json()["results"]
    assert len(response_results) == 2

    response_count = household_list_context["api_client"].get(household_list_context["count_url"])
    assert response_count.status_code == status.HTTP_200_OK
    assert response_count.json()["count"] == 2

    response_ids = [result["id"] for result in response_results]
    assert str(household_list_context["household1"].id) in response_ids
    assert str(household_list_context["household2"].id) in response_ids

    for i, household in enumerate([household_list_context["household1"], household_list_context["household2"]]):
        household_result = response_results[i]
        assert household_result["id"] == str(household.id)
        assert household_result["unicef_id"] == household.unicef_id
        assert household_result["head_of_household"] == household.head_of_household.full_name
        assert household_result["admin1"] == {
            "id": str(household.admin1.id),
            "name": household.admin1.name,
        }
        assert household_result["admin2"] == {
            "id": str(household.admin2.id),
            "name": household.admin2.name,
        }

        assert household_result["program_id"] == str(household.program.id)
        assert household_result["program_name"] == household.program.name
        assert household_result["status"] == household.status
        assert household_result["size"] == household.size
        assert household_result["residence_status"] == household.get_residence_status_display()
        assert household_result["total_cash_received"] == household.total_cash_received
        assert household_result["total_cash_received_usd"] == household.total_cash_received_usd
        assert household_result["last_registration_date"] == f"{household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"


def test_household_count_with_permissions(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )
    response = household_list_context["api_client"].get(household_list_context["count_url"])
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 2


def test_household_count_without_permissions(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )
    response = household_list_context["api_client"].get(household_list_context["count_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        (Permissions.PROGRAMME_ACTIVATE,),
    ],
)
def test_household_list_without_permissions(
    permissions: list,
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=permissions,
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )

    response = household_list_context["api_client"].get(household_list_context["list_url"])
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_household_list_on_draft_program(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    program = ProgramFactory(business_area=household_list_context["afghanistan"], status=Program.DRAFT)
    list_url = reverse(
        "api:households:households-list",
        kwargs={
            "business_area_slug": household_list_context["afghanistan"].slug,
            "program_slug": program.slug,
        },
    )
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=program,
    )
    for _ in range(2):
        household = HouseholdFactory(
            admin1=household_list_context["area1"],
            admin2=household_list_context["area2"],
            country_origin=household_list_context["country"],
            program=program,
            business_area=household_list_context["afghanistan"],
            size=2,
        )
        IndividualFactory(
            household=household,
            business_area=household_list_context["afghanistan"],
            program=program,
            registration_data_import=household.registration_data_import,
        )

    response = household_list_context["api_client"].get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 0


def test_household_list_with_admin_area_limits(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    set_admin_area_limits_in_program: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )
    set_admin_area_limits_in_program(
        household_list_context["partner"], household_list_context["program"], [household_list_context["area1"]]
    )

    household_without_areas = HouseholdFactory(
        country_origin=household_list_context["country"],
        program=household_list_context["program"],
        business_area=household_list_context["afghanistan"],
        admin1=None,
        admin2=None,
    )
    area_different = AreaFactory(parent=None, p_code="AF05", area_type=household_list_context["area1"].area_type)
    household_different_areas = HouseholdFactory(
        admin1=household_list_context["area1"],
        admin2=household_list_context["area2"],
        country_origin=household_list_context["country"],
        program=household_list_context["program"],
        business_area=household_list_context["afghanistan"],
        size=2,
    )
    IndividualFactory(
        household=household_different_areas,
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
        registration_data_import=household_different_areas.registration_data_import,
    )
    household_different_areas.admin1 = area_different
    household_different_areas.admin2 = area_different
    household_different_areas.save()

    response = household_list_context["api_client"].get(household_list_context["list_url"])
    assert response.status_code == status.HTTP_200_OK
    response_results = response.data["results"]
    assert len(response_results) == 3

    response_ids = [result["id"] for result in response_results]

    assert str(household_list_context["household1"].id) in response_ids
    assert str(household_list_context["household2"].id) in response_ids
    assert str(household_without_areas.id) in response_ids

    assert str(household_different_areas.id) not in response_ids


def test_household_list_caching(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
    set_admin_area_limits_in_program: Any,
) -> None:
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.RDI_VIEW_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )

    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag = response.headers["etag"]
        assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
        assert len(response.json()["results"]) == 2
        assert len(ctx.captured_queries) == 16

    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_second_call = response.headers["etag"]
        assert etag == etag_second_call
        assert len(ctx.captured_queries) == 8

    household_list_context["household1"].children_count = 100
    household_list_context["household1"].save(update_fields=["children_count"])
    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_third_call = response.headers["etag"]
        assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
        assert etag_third_call not in [etag, etag_second_call]
        assert len(ctx.captured_queries) == 11

    set_admin_area_limits_in_program(
        household_list_context["partner"],
        household_list_context["program"],
        [household_list_context["area1"]],
    )
    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_changed_areas = response.headers["etag"]
        assert json.loads(cache.get(etag_changed_areas)[0].decode("utf8")) == response.json()
        assert etag_changed_areas not in [etag, etag_second_call, etag_third_call]
        assert len(ctx.captured_queries) == 11

    household_list_context["household2"].delete()
    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fourth_call = response.headers["etag"]
        assert len(response.json()["results"]) == 1
        assert etag_fourth_call not in [etag, etag_second_call, etag_third_call, etag_changed_areas]
        assert len(ctx.captured_queries) == 11

    with CaptureQueriesContext(connection) as ctx:
        response = household_list_context["api_client"].get(household_list_context["list_url"])
        assert response.status_code == status.HTTP_200_OK
        assert response.has_header("etag")
        etag_fifth_call = response.headers["etag"]
        assert etag_fifth_call == etag_fourth_call
        assert len(ctx.captured_queries) == 8


def test_household_all_flex_fields_attributes(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    program = ProgramFactory(business_area=household_list_context["afghanistan"], status=Program.DRAFT)
    list_url = reverse(
        "api:households:households-all-flex-fields-attributes",
        kwargs={
            "business_area_slug": household_list_context["afghanistan"].slug,
            "program_slug": program.slug,
        },
    )
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=program,
    )
    FlexibleAttributeFactory(
        name="Flexible Attribute for HH",
        type=FlexibleAttribute.STRING,
        label={"English(EN)": "Test Flex", "Test": ""},
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
        program=program,
    )

    response = household_list_context["api_client"].get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Flexible Attribute for HH"


def test_household_all_accountability_communication_message_recipients(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    household_list_context["household1"].head_of_household.phone_no_valid = True
    household_list_context["household2"].head_of_household.phone_no_alternative_valid = True
    household_list_context["household1"].head_of_household.save(update_fields=["phone_no_valid"])
    household_list_context["household2"].head_of_household.save(update_fields=["phone_no_alternative_valid"])

    list_url = reverse(
        "api:households:households-all-accountability-communication-message-recipients",
        kwargs={
            "business_area_slug": household_list_context["afghanistan"].slug,
            "program_slug": household_list_context["program"].slug,
        },
    )
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.ACCOUNTABILITY_COMMUNICATION_MESSAGE_VIEW_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )

    response = household_list_context["api_client"].get(list_url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2

    survey = SurveyFactory(created_by=household_list_context["user"])
    survey.recipients.set([household_list_context["household1"]])

    response = household_list_context["api_client"].get(list_url, {"survey_id": str(survey.pk)})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    recipient_1_results = response.json()["results"][0]
    assert recipient_1_results == {
        "id": str(household_list_context["household1"].pk),
        "unicef_id": household_list_context["household1"].unicef_id,
        "size": household_list_context["household1"].size,
        "head_of_household": {
            "id": str(household_list_context["household1"].head_of_household.pk),
            "full_name": household_list_context["household1"].head_of_household.full_name,
        },
        "admin2": {
            "id": str(household_list_context["household1"].admin2.pk),
            "name": household_list_context["household1"].admin2.name,
        },
        "status": household_list_context["household1"].status,
        "residence_status": household_list_context["household1"].get_residence_status_display(),
        "last_registration_date": f"{household_list_context['household1'].last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
    }


def test_household_recipients(
    household_list_context: dict[str, Any],
    create_user_role_with_permissions: Any,
) -> None:
    list_url = reverse(
        "api:households:households-recipients",
        kwargs={
            "business_area_slug": household_list_context["afghanistan"].slug,
            "program_slug": household_list_context["program"].slug,
        },
    )
    create_user_role_with_permissions(
        user=household_list_context["user"],
        permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_DETAILS],
        business_area=household_list_context["afghanistan"],
        program=household_list_context["program"],
    )
    msg_obj = CommunicationMessageFactory(business_area=household_list_context["afghanistan"])
    msg_obj.households.set([household_list_context["household1"], household_list_context["household2"]])

    response = household_list_context["api_client"].get(list_url, {"message_id": str(msg_obj.pk)})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 2

    response = household_list_context["api_client"].get(
        list_url,
        {
            "message_id": str(msg_obj.pk),
            "recipient_id": str(household_list_context["household1"].head_of_household.pk),
        },
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["id"] == str(household_list_context["household1"].pk)


@pytest.fixture
def household_detail_context(api_client: Any) -> dict[str, Any]:
    detail_url_name = "api:households:households-detail"

    afghanistan = BusinessAreaFactory(slug="afghanistan", name="Afghanistan")
    program = ProgramFactory(business_area=afghanistan, status=Program.ACTIVE)
    partner = PartnerFactory(name="TestPartner")
    user = UserFactory(partner=partner)
    client = api_client(user)

    country = CountryFactory()
    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)

    area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
    area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
    area3 = AreaFactory(parent=area2, p_code="AF010101", area_type=admin_type_2)
    area4 = AreaFactory(parent=area3, p_code="AF01010101", area_type=admin_type_2)

    registration_data_import = RegistrationDataImportFactory(
        imported_by=user, business_area=afghanistan, program=program
    )
    geopoint = [51.107883, 17.038538]
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
        geopoint=geopoint,
        start=timezone.now(),
        create_role=False,
    )
    individual_primary = household.head_of_household
    individual_secondary = IndividualFactory(
        household=household,
        business_area=afghanistan,
        program=program,
        registration_data_import=registration_data_import,
    )
    primary_role = IndividualRoleInHouseholdFactory(
        individual=individual_primary,
        household=household,
        role=ROLE_PRIMARY,
    )

    individual_secondary.deduplication_golden_record_status = DUPLICATE
    individual_secondary.duplicate = True
    individual_secondary.save(update_fields=["deduplication_golden_record_status", "duplicate"])

    grievance_ticket = GrievanceTicketFactory(household_unicef_id=household.unicef_id)
    GrievanceTicketFactory()

    program_cycle = ProgramCycleFactory(program=program)
    PaymentFactory(
        parent=PaymentPlanFactory(program_cycle=program_cycle, business_area=afghanistan),
        currency="AFG",
        delivered_quantity_usd=50,
        delivered_quantity=100,
        household=household,
        collector=household.head_of_household,
        status=Payment.STATUS_SUCCESS,
    )
    PaymentFactory(
        parent=PaymentPlanFactory(program_cycle=program_cycle, business_area=afghanistan),
        currency="AFG",
        delivered_quantity_usd=33,
        delivered_quantity=133,
        household=household,
        collector=household.head_of_household,
    )

    return {
        "detail_url_name": detail_url_name,
        "afghanistan": afghanistan,
        "program": program,
        "partner": partner,
        "user": user,
        "api_client": client,
        "country": country,
        "area1": area1,
        "area2": area2,
        "area3": area3,
        "area4": area4,
        "registration_data_import": registration_data_import,
        "geopoint": geopoint,
        "household": household,
        "individuals": [individual_primary, individual_secondary],
        "primary_role": primary_role,
        "grievance_ticket": grievance_ticket,
    }


@pytest.mark.parametrize(
    "permissions",
    [
        (Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS,),
        (Permissions.RDI_VIEW_DETAILS,),
    ],
)
def test_household_detail_with_permissions(
    permissions: list, create_user_role_with_permissions: Any, household_detail_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_detail_context["user"],
        permissions=permissions,
        business_area=household_detail_context["afghanistan"],
        program=household_detail_context["program"],
    )
    response = household_detail_context["api_client"].get(
        reverse(
            household_detail_context["detail_url_name"],
            kwargs={
                "business_area_slug": household_detail_context["afghanistan"].slug,
                "program_slug": household_detail_context["program"].slug,
                "pk": str(household_detail_context["household"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.data
    household = household_detail_context["household"]
    individuals = household_detail_context["individuals"]
    primary_role = household_detail_context["primary_role"]
    registration_data_import = household_detail_context["registration_data_import"]
    grievance_ticket = household_detail_context["grievance_ticket"]

    assert data["id"] == str(household.id)
    assert data["unicef_id"] == household.unicef_id
    assert data["head_of_household"] == {
        "id": str(individuals[0].id),
        "full_name": individuals[0].full_name,
    }
    assert data["admin1"] == {
        "id": str(household.admin1.id),
        "name": household.admin1.name,
    }
    assert data["admin2"] == {
        "id": str(household.admin2.id),
        "name": household.admin2.name,
    }
    assert data["admin3"] == {
        "id": str(household.admin3.id),
        "name": household.admin3.name,
    }
    assert data["admin4"] == {
        "id": str(household.admin4.id),
        "name": household.admin4.name,
    }
    assert data["program"] == household.program.name
    assert data["country"] == household.country.name
    assert data["country_origin"] == household.country_origin.name
    assert data["status"] == household.status
    assert data["total_cash_received"] == household.total_cash_received
    assert data["total_cash_received_usd"] == household.total_cash_received_usd
    assert data["has_duplicates"] is True
    assert data["registration_data_import"] == {
        "id": str(registration_data_import.id),
        "name": registration_data_import.name,
        "status": registration_data_import.status,
        "import_date": f"{registration_data_import.import_date:%Y-%m-%dT%H:%M:%SZ}",
        "number_of_individuals": registration_data_import.number_of_individuals,
        "number_of_households": registration_data_import.number_of_households,
        "imported_by": {
            "id": str(registration_data_import.imported_by.id),
            "first_name": registration_data_import.imported_by.first_name,
            "last_name": registration_data_import.imported_by.last_name,
            "email": registration_data_import.imported_by.email,
            "username": registration_data_import.imported_by.username,
        },
        "data_source": registration_data_import.data_source,
    }
    assert data["flex_fields"] == resolve_flex_fields_choices_to_string(household)
    assert data["admin_area_title"] == f"{household.admin4.name} - {household.admin4.p_code}"
    assert data["active_individuals_count"] == 1
    assert data["geopoint"] == household.geopoint
    assert data["import_id"] == household.unicef_id
    assert data["admin_url"] is None
    assert data["male_children_count"] == household.male_children_count
    assert data["female_children_count"] == household.female_children_count
    assert data["children_disabled_count"] == household.children_disabled_count
    assert data["currency"] == household.currency
    assert data["first_registration_date"] == f"{household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}"
    assert data["last_registration_date"] == f"{household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}"
    assert data["unhcr_id"] == household.unhcr_id
    assert data["village"] == household.village
    assert data["address"] == household.address
    assert data["zip_code"] == household.zip_code
    assert data["female_age_group_0_5_count"] == household.female_age_group_0_5_count
    assert data["female_age_group_6_11_count"] == household.female_age_group_6_11_count
    assert data["female_age_group_12_17_count"] == household.female_age_group_12_17_count
    assert data["female_age_group_18_59_count"] == household.female_age_group_18_59_count
    assert data["female_age_group_60_count"] == household.female_age_group_60_count
    assert data["pregnant_count"] == household.pregnant_count
    assert data["male_age_group_0_5_count"] == household.male_age_group_0_5_count
    assert data["male_age_group_6_11_count"] == household.male_age_group_6_11_count
    assert data["male_age_group_12_17_count"] == household.male_age_group_12_17_count
    assert data["male_age_group_18_59_count"] == household.male_age_group_18_59_count
    assert data["male_age_group_60_count"] == household.male_age_group_60_count
    assert data["female_age_group_0_5_disabled_count"] == household.female_age_group_0_5_disabled_count
    assert data["female_age_group_6_11_disabled_count"] == household.female_age_group_6_11_disabled_count
    assert data["female_age_group_12_17_disabled_count"] == household.female_age_group_12_17_disabled_count
    assert data["female_age_group_18_59_disabled_count"] == household.female_age_group_18_59_disabled_count
    assert data["female_age_group_60_disabled_count"] == household.female_age_group_60_disabled_count
    assert data["male_age_group_0_5_disabled_count"] == household.male_age_group_0_5_disabled_count
    assert data["male_age_group_6_11_disabled_count"] == household.male_age_group_6_11_disabled_count
    assert data["male_age_group_12_17_disabled_count"] == household.male_age_group_12_17_disabled_count
    assert data["male_age_group_18_59_disabled_count"] == household.male_age_group_18_59_disabled_count
    assert data["male_age_group_60_disabled_count"] == household.male_age_group_60_disabled_count
    assert data["other_sex_group_count"] == household.other_sex_group_count
    assert data["start"] == f"{household.start:%Y-%m-%dT%H:%M:%SZ}"
    assert data["deviceid"] == household.deviceid
    assert data["fchild_hoh"] == household.fchild_hoh
    assert data["child_hoh"] == household.child_hoh
    assert data["returnee"] == household.returnee
    assert data["size"] == household.size
    assert data["residence_status"] == household.get_residence_status_display()
    assert data["program_registration_id"] == household.program_registration_id
    assert data["delivered_quantities"] == [
        {
            "currency": "USD",
            "total_delivered_quantity": "83.00",
        },
        {
            "currency": "AFG",
            "total_delivered_quantity": "233.00",
        },
    ]
    assert data["linked_grievances"] == [
        {
            "id": str(grievance_ticket.id),
            "category": grievance_ticket.category,
            "status": grievance_ticket.status,
        }
    ]
    assert data["consent"] == household.consent
    assert data["name_enumerator"] == household.name_enumerator
    assert data["org_enumerator"] == household.org_enumerator
    assert data["org_name_enumerator"] == household.org_name_enumerator
    assert data["registration_method"] == household.registration_method
    assert data["consent_sharing"] == list(household.consent_sharing)
    assert data["roles_in_household"] == [
        {
            "id": str(primary_role.id),
            "role": ROLE_PRIMARY,
            "individual": {
                "id": str(individuals[0].id),
                "unicef_id": individuals[0].unicef_id,
            },
        }
    ]


def test_household_detail_admin_url(household_detail_context: dict[str, Any]) -> None:
    user = household_detail_context["user"]
    user.is_superuser = True
    user.save(update_fields=["is_superuser"])

    response = household_detail_context["api_client"].get(
        reverse(
            household_detail_context["detail_url_name"],
            kwargs={
                "business_area_slug": household_detail_context["afghanistan"].slug,
                "program_slug": household_detail_context["program"].slug,
                "pk": str(household_detail_context["household"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["admin_url"] == household_detail_context["household"].admin_url


@pytest.mark.parametrize(
    "permissions",
    [
        [],
        (Permissions.PROGRAMME_ACTIVATE,),
    ],
)
def test_household_detail_without_permissions(
    permissions: list, create_user_role_with_permissions: Any, household_detail_context: dict[str, Any]
) -> None:
    create_user_role_with_permissions(
        user=household_detail_context["user"],
        permissions=permissions,
        business_area=household_detail_context["afghanistan"],
        program=household_detail_context["program"],
    )
    response = household_detail_context["api_client"].get(
        reverse(
            household_detail_context["detail_url_name"],
            kwargs={
                "business_area_slug": household_detail_context["afghanistan"].slug,
                "program_slug": household_detail_context["program"].slug,
                "pk": str(household_detail_context["household"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_household_detail_with_permissions_in_different_program(
    create_user_role_with_permissions: Any, household_detail_context: dict[str, Any]
) -> None:
    program_other = ProgramFactory(
        name="Program Other",
        business_area=household_detail_context["afghanistan"],
        status=Program.ACTIVE,
    )
    create_user_role_with_permissions(
        user=household_detail_context["user"],
        permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS],
        business_area=household_detail_context["afghanistan"],
        program=program_other,
    )
    response = household_detail_context["api_client"].get(
        reverse(
            household_detail_context["detail_url_name"],
            kwargs={
                "business_area_slug": household_detail_context["afghanistan"].slug,
                "program_slug": household_detail_context["program"].slug,
                "pk": str(household_detail_context["household"].id),
            },
        )
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
