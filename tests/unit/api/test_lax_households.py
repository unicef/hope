import os
import tempfile
from typing import Any
from unittest.mock import patch

from django.core.files.storage import default_storage
from django.test.utils import override_settings
import pytest
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from extras.test_utils.factories import (
    APITokenFactory,
    AreaFactory,
    AreaTypeFactory,
    BusinessAreaFactory,
    CountryFactory,
    FlexibleAttributeFactory,
    HouseholdFactory,
    PendingIndividualFactory,
    RegistrationDataImportFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from hope.apps.program.collision_detectors import IdentificationKeyCollisionDetector
from hope.models import (
    Area,
    BusinessArea,
    Country,
    Facility,
    FlexibleAttribute,
    Household,
    PendingHousehold,
    PendingIndividual,
    Program,
    RegistrationDataImport,
)
from hope.models.grant import Grant

pytestmark = pytest.mark.django_db


# ── Core fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def business_area() -> BusinessArea:
    return BusinessAreaFactory(slug="afghanistan")


@pytest.fixture
def rdi(business_area: BusinessArea) -> RegistrationDataImport:
    return RegistrationDataImportFactory(
        business_area=business_area,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
        program__status=Program.DRAFT,
    )


@pytest.fixture
def program(rdi: RegistrationDataImport) -> Program:
    return rdi.program


@pytest.fixture
def pakistan_country() -> Country:
    return CountryFactory(name="Pakistan", short_name="Pakistan", iso_code2="PK", iso_code3="PAK", iso_num="0586")


@pytest.fixture
def api_client(business_area: BusinessArea) -> APIClient:
    user = UserFactory()
    role = RoleFactory(name="API Role", permissions=[Grant.API_RDI_CREATE.name])
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    token = APITokenFactory(user=user, grants=[Grant.API_RDI_CREATE.name])
    token.valid_for.set([business_area])
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION="Token " + token.key)
    return client


@pytest.fixture
def lax_households_url(business_area: BusinessArea, rdi: RegistrationDataImport) -> str:
    return reverse("api:rdi-push-lax-households", args=[business_area.slug, str(rdi.id)])


# ── Individual fixtures ────────────────────────────────────────────────


@pytest.fixture
def head_of_household(rdi: RegistrationDataImport) -> PendingIndividual:
    return PendingIndividualFactory(
        individual_id="IND001",
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


@pytest.fixture
def primary_collector(rdi: RegistrationDataImport) -> PendingIndividual:
    return PendingIndividualFactory(
        individual_id="IND002",
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


@pytest.fixture
def alternate_collector(rdi: RegistrationDataImport) -> PendingIndividual:
    return PendingIndividualFactory(
        individual_id="IND003",
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


@pytest.fixture
def second_hoh(rdi: RegistrationDataImport) -> PendingIndividual:
    return PendingIndividualFactory(
        individual_id="IND004",
        registration_data_import=rdi,
        program=rdi.program,
        business_area=rdi.business_area,
    )


# ── Admin area fixtures ───────────────────────────────────────────────


@pytest.fixture
def admin1(afghanistan_country: Country) -> Area:
    admin_type = AreaTypeFactory(country=afghanistan_country, area_level=1)
    return AreaFactory(parent=None, p_code="AF01", area_type=admin_type)


@pytest.fixture
def admin2(admin1: Area, afghanistan_country: Country) -> Area:
    admin_type = AreaTypeFactory(country=afghanistan_country, area_level=2, parent=admin1.area_type)
    return AreaFactory(parent=admin1, p_code="AF0101", area_type=admin_type)


@pytest.fixture
def admin3(admin2: Area, afghanistan_country: Country) -> Area:
    admin_type = AreaTypeFactory(country=afghanistan_country, area_level=3, parent=admin2.area_type)
    return AreaFactory(parent=admin2, p_code="AF010101", area_type=admin_type)


@pytest.fixture
def admin4(admin3: Area, afghanistan_country: Country) -> Area:
    admin_type = AreaTypeFactory(country=afghanistan_country, area_level=4, parent=admin3.area_type)
    return AreaFactory(parent=admin3, p_code="AF01010101", area_type=admin_type)


# ── Collision fixture ──────────────────────────────────────────────────


@pytest.fixture
def collision_program(program: Program) -> Program:
    program.collision_detector = IdentificationKeyCollisionDetector
    program.save(update_fields=["collision_detector"])
    return program


@pytest.fixture
def existing_collision_household(business_area: BusinessArea, collision_program: Program) -> Household:
    return HouseholdFactory(
        business_area=business_area,
        program=collision_program,
        identification_key="COLLISION-KEY-001",
    )


@pytest.fixture
def existing_collision_household_a(business_area: BusinessArea, collision_program: Program) -> Household:
    return HouseholdFactory(
        business_area=business_area,
        program=collision_program,
        identification_key="COLLISION-KEY-A",
    )


@pytest.fixture
def existing_collision_household_b(business_area: BusinessArea, collision_program: Program) -> Household:
    return HouseholdFactory(
        business_area=business_area,
        program=collision_program,
        identification_key="COLLISION-KEY-B",
    )


@pytest.fixture
def household_image_flex_attribute() -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="household_photo_h_f",
        label={"English(EN)": "Household Photo"},
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
    )


# ── Tests ──────────────────────────────────────────────────────────────


def test_create_household_success(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    alternate_collector: PendingIndividual,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 3,
        "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "alternate_collector": alternate_collector.unicef_id,
        "members": [
            head_of_household.unicef_id,
            primary_collector.unicef_id,
            alternate_collector.unicef_id,
        ],
        "originating_id": "KOB#123#123",
    }

    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
    assert household.country.iso_code2 == "AF"
    assert household.country_origin.iso_code2 == "AF"
    assert household.size == 3
    assert sorted(household.consent_sharing) == sorted(["UNICEF", "PRIVATE_PARTNER"])
    assert household.village == "Test Village"
    assert household.originating_id == "KOB#123#123"
    assert household.head_of_household == head_of_household
    assert household.primary_collector == primary_collector
    assert household.alternate_collector == alternate_collector


def test_create_multiple_households_success(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    pakistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    alternate_collector: PendingIndividual,
    second_hoh: PendingIndividual,
) -> None:
    payloads = [
        {
            "country": "AF",
            "country_origin": "AF",
            "size": 3,
            "consent_sharing": ["UNICEF"],
            "village": "Village 1",
            "head_of_household": head_of_household.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "alternate_collector": alternate_collector.unicef_id,
            "members": [head_of_household.unicef_id, primary_collector.unicef_id],
        },
        {
            "country": "PK",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
            "village": "Village 2",
            "head_of_household": second_hoh.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "members": [head_of_household.unicef_id],
        },
    ]

    response = api_client.post(lax_households_url, payloads, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 2
    assert response.data["errors"] == 0


def test_create_household_with_validation_errors(
    api_client: APIClient,
    lax_households_url: str,
) -> None:
    payloads = [
        {
            "country": "INVALID_COUNTRY",
            "size": -1,
            "head_of_household": "NON_EXISTENT_ID",
            "primary_collector": "NON_EXISTENT_ID",
            "members": [],
        },
    ]

    response = api_client.post(lax_households_url, payloads, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 0
    assert response.data["errors"] == 1


def test_create_households_mixed_success_and_errors(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
) -> None:
    payloads = [
        {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF"],
            "village": "Valid Village",
            "head_of_household": head_of_household.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "members": [head_of_household.unicef_id],
        },
        {
            "country": "INVALID_COUNTRY",
            "size": -1,
            "head_of_household": "NON_EXISTENT_ID",
            "primary_collector": "NON_EXISTENT_ID",
            "members": [],
        },
    ]

    response = api_client.post(lax_households_url, payloads, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 1


def test_household_with_admin_areas(
    api_client: APIClient,
    lax_households_url: str,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    alternate_collector: PendingIndividual,
    admin1: Area,
    admin2: Area,
    admin3: Area,
    admin4: Area,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 2,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "alternate_collector": alternate_collector.unicef_id,
        "members": [head_of_household.unicef_id, primary_collector.unicef_id],
        "admin1": admin1.p_code,
        "admin2": admin2.p_code,
        "admin3": admin3.p_code,
        "admin4": admin4.p_code,
    }

    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0

    household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
    assert household.admin1 == admin1
    assert household.admin2 == admin2
    assert household.admin3 == admin3
    assert household.admin4 == admin4


def test_collision_detected_household_added_to_extra_rdis(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    existing_collision_household: Household,
    rdi: RegistrationDataImport,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "identification_key": "COLLISION-KEY-001",
    }

    hh_count_before = PendingHousehold.objects.count()
    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 1
    assert response.data["accepted"] == 1
    assert response.data["errors"] == 0
    assert PendingHousehold.objects.count() == hh_count_before
    rdi.refresh_from_db()
    assert rdi.extra_hh_rdis.filter(id=existing_collision_household.id).exists()


def test_collision_only_batch_returns_early(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    second_hoh: PendingIndividual,
    existing_collision_household_a: Household,
    existing_collision_household_b: Household,
    rdi: RegistrationDataImport,
) -> None:
    households_data = [
        {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF"],
            "village": "Village A",
            "head_of_household": head_of_household.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "members": [head_of_household.unicef_id],
            "identification_key": "COLLISION-KEY-A",
        },
        {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF"],
            "village": "Village B",
            "head_of_household": second_hoh.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "members": [second_hoh.unicef_id],
            "identification_key": "COLLISION-KEY-B",
        },
    ]

    hh_count_before = PendingHousehold.objects.count()
    response = api_client.post(lax_households_url, households_data, format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["processed"] == 2
    assert response.data["accepted"] == 2
    assert response.data["errors"] == 0
    assert PendingHousehold.objects.count() == hh_count_before
    rdi.refresh_from_db()
    assert rdi.extra_hh_rdis.filter(id=existing_collision_household_a.id).exists()
    assert rdi.extra_hh_rdis.filter(id=existing_collision_household_b.id).exists()


def test_create_household_with_consent_sign_stores_image_file(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    program: Program,
    base64_image: str,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "consent_sign": base64_image,
    }

    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1

    household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
    programme_code = program.code
    assert household.consent_sign.name.startswith(programme_code)
    assert household.consent_sign.name.endswith(".png")
    assert default_storage.exists(household.consent_sign.name)


def test_consent_sign_cleanup_on_failure(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    rdi: RegistrationDataImport,
    base64_image: str,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "consent_sign": base64_image,
    }

    with tempfile.TemporaryDirectory() as media_root:
        with override_settings(MEDIA_ROOT=media_root):

            def fail_after_files_exist(*args: Any, **kwargs: Any) -> None:
                pre_cleanup_files = []
                for root, _, files in os.walk(media_root):
                    pre_cleanup_files.extend(os.path.join(root, f) for f in files)
                assert len(pre_cleanup_files) > 0
                raise RuntimeError("forced failure for consent sign cleanup test")

            with patch(
                "hope.api.endpoints.rdi.lax.PendingHousehold.objects.bulk_create",
                side_effect=fail_after_files_exist,
            ):
                response = api_client.post(lax_households_url, [household_data], format="json")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Failed to create lax households.",
                "rdi_id": str(rdi.id),
            }

            leftover_files = []
            for root, _, files in os.walk(media_root):
                leftover_files.extend(os.path.join(root, f) for f in files)
            assert leftover_files == []


def test_household_with_image_flex_field(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    household_image_flex_attribute: FlexibleAttribute,
    base64_image: str,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "household_photo": base64_image,
    }

    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1

    household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
    assert "household_photo" in household.flex_fields
    assert not household.flex_fields["household_photo"].startswith(base64_image[:20])
    assert default_storage.exists(household.flex_fields["household_photo"])


def test_household_image_flex_field_cleanup_on_failure(
    api_client: APIClient,
    lax_households_url: str,
    afghanistan_country: Country,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    rdi: RegistrationDataImport,
    household_image_flex_attribute: FlexibleAttribute,
    base64_image: str,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "household_photo": base64_image,
    }

    with tempfile.TemporaryDirectory() as media_root:
        with override_settings(MEDIA_ROOT=media_root):

            def fail_after_files_exist(*args: Any, **kwargs: Any) -> None:
                pre_cleanup_files = []
                for root, _, files in os.walk(media_root):
                    pre_cleanup_files.extend(os.path.join(root, f) for f in files)
                assert len(pre_cleanup_files) > 0
                raise RuntimeError("forced failure for image flex field cleanup test")

            with patch(
                "hope.api.endpoints.rdi.lax.PendingHousehold.objects.bulk_create",
                side_effect=fail_after_files_exist,
            ):
                response = api_client.post(lax_households_url, [household_data], format="json")

            assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert response.json() == {
                "detail": "Failed to create lax households.",
                "rdi_id": str(rdi.id),
            }

            leftover_files = []
            for root, _, files in os.walk(media_root):
                leftover_files.extend(os.path.join(root, f) for f in files)
            assert leftover_files == []


def test_household_create_validation_facility_area(
    api_client: APIClient,
    lax_households_url: str,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    afghanistan_country: Country,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "facility_name": "NEW Org",
    }
    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert (
        "This field is required when facility_name is provided." in response.json()["results"][0]["facility_admin_area"]
    )


def test_household_create_facility(
    api_client: APIClient,
    lax_households_url: str,
    head_of_household: PendingIndividual,
    primary_collector: PendingIndividual,
    admin1: Area,
    afghanistan_country: Country,
) -> None:
    household_data = {
        "country": "AF",
        "country_origin": "AF",
        "size": 1,
        "consent_sharing": ["UNICEF"],
        "village": "Test Village",
        "head_of_household": head_of_household.unicef_id,
        "primary_collector": primary_collector.unicef_id,
        "members": [head_of_household.unicef_id],
        "facility_name": "NEW Org Lax TEST",
        "facility_admin_area": "AF01",
    }
    response = api_client.post(lax_households_url, [household_data], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1
    assert Facility.objects.count() == 1
    assert PendingHousehold.objects.first().facility.name == "NEW ORG LAX TEST"
    assert Facility.objects.first().name == "NEW ORG LAX TEST"
    assert Facility.objects.first().admin_area.p_code == "AF01"
