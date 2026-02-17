import base64
import os
from pathlib import Path
import tempfile
from typing import Any
from unittest.mock import patch

from django.core.files.storage import default_storage
from django.test.utils import override_settings
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.core import FlexibleAttributeFactory
from extras.test_utils.old_factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.old_factories.household import PendingIndividualFactory
from extras.test_utils.old_factories.program import ProgramFactory
from extras.test_utils.old_factories.registration_data import RegistrationDataImportFactory
from hope.models import FlexibleAttribute, PendingHousehold, Program, RegistrationDataImport
from hope.models.utils import Grant
from unit.api.base import HOPEApiTestCase
from unit.api.factories import APITokenFactory


class CreateLaxHouseholdsTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        # Create only countries needed by test (AF, PK)
        country = CountryFactory(
            name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"
        )
        CountryFactory(name="Pakistan", short_name="Pakistan", iso_code2="PK", iso_code3="PAK", iso_num="0586")
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)
        admin_type_4 = AreaTypeFactory(country=country, area_level=4, parent=admin_type_3)

        cls.admin1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        cls.admin2 = AreaFactory(parent=cls.admin1, p_code="AF0101", area_type=admin_type_2)
        cls.admin3 = AreaFactory(parent=cls.admin2, p_code="AF010101", area_type=admin_type_3)
        cls.admin4 = AreaFactory(parent=cls.admin3, p_code="AF01010101", area_type=admin_type_4)

        image = Path(__file__).parent / "logo.png"
        cls.base64_encoded_data = base64.b64encode(image.read_bytes()).decode("utf-8")

    def setUp(self) -> None:
        super().setUp()
        self.program = ProgramFactory(status=Program.DRAFT, business_area=self.business_area)

        self.rdi: RegistrationDataImport = RegistrationDataImportFactory(
            business_area=self.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=self.program,
        )
        self.url = reverse("api:rdi-push-lax-households", args=[self.business_area.slug, str(self.rdi.id)])
        self.head_of_household = PendingIndividualFactory(
            individual_id="IND001",
            registration_data_import=self.rdi,
            program=self.program,
            business_area=self.business_area,
        )
        self.primary_collector = PendingIndividualFactory(
            individual_id="IND002",
            registration_data_import=self.rdi,
            program=self.program,
            business_area=self.business_area,
        )
        self.alternate_collector = PendingIndividualFactory(
            individual_id="IND003",
            registration_data_import=self.rdi,
            program=self.program,
            business_area=self.business_area,
        )

    def test_create_single_household_success(self) -> None:
        household_data = {
            "country": "AF",
            "country_origin": "AF",
            "size": 3,
            "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
            "village": "Test Village",
            "head_of_household": self.head_of_household.unicef_id,
            "primary_collector": self.primary_collector.unicef_id,
            "alternate_collector": self.alternate_collector.unicef_id,
            "members": [
                self.head_of_household.unicef_id,
                self.primary_collector.unicef_id,
                self.alternate_collector.unicef_id,
            ],
        }

        response = self.client.post(self.url, [household_data], format="json")

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
        assert household.head_of_household == self.head_of_household
        assert household.primary_collector == self.primary_collector
        assert household.alternate_collector == self.alternate_collector

    def test_create_multiple_households_success(self) -> None:
        second_head_of_household = PendingIndividualFactory(
            individual_id="IND004",
            registration_data_import=self.rdi,
            program=self.program,
            business_area=self.business_area,
        )
        households_data = [
            {
                "country": "AF",
                "country_origin": "AF",
                "size": 3,
                "consent_sharing": ["UNICEF"],
                "village": "Village 1",
                "head_of_household": self.head_of_household.unicef_id,
                "primary_collector": self.primary_collector.unicef_id,
                "alternate_collector": self.alternate_collector.unicef_id,
                "members": [self.head_of_household.unicef_id, self.primary_collector.unicef_id],
            },
            {
                "country": "PK",
                "country_origin": "AF",
                "size": 1,
                "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
                "village": "Village 2",
                "head_of_household": second_head_of_household.unicef_id,
                "primary_collector": self.primary_collector.unicef_id,
                "members": [self.head_of_household.unicef_id],
            },
        ]

        response = self.client.post(self.url, households_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 2
        assert response.data["accepted"] == 2
        assert response.data["errors"] == 0

    def test_create_household_with_validation_errors(self) -> None:
        household_data = {
            "country": "INVALID_COUNTRY",
            "size": -1,
            "head_of_household": "NON_EXISTENT_ID",
            "primary_collector": "NON_EXISTENT_ID",
            "members": [],
        }

        response = self.client.post(self.url, [household_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 0
        assert response.data["errors"] == 1

    def test_create_households_mixed_success_and_errors(self) -> None:
        households_data = [
            {
                "country": "AF",
                "country_origin": "AF",
                "size": 1,
                "consent_sharing": ["UNICEF"],
                "village": "Valid Village",
                "head_of_household": self.head_of_household.unicef_id,
                "primary_collector": self.primary_collector.unicef_id,
                "members": [self.head_of_household.unicef_id],
            },
            {
                "country": "INVALID_COUNTRY",
                "size": -1,
                "head_of_household": "NON_EXISTENT_ID",
                "primary_collector": "NON_EXISTENT_ID",
                "members": [],
            },
        ]

        response = self.client.post(self.url, households_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 2
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 1

    def test_household_without_alternate_collector(self) -> None:
        household_data = {
            "country": "AF",
            "country_origin": "AF",
            "size": 2,
            "consent_sharing": ["UNICEF"],
            "village": "Test Village",
            "head_of_household": self.head_of_household.unicef_id,
            "primary_collector": self.primary_collector.unicef_id,
            "members": [self.head_of_household.unicef_id, self.primary_collector.unicef_id],
        }

        response = self.client.post(self.url, [household_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 0

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        assert household.alternate_collector is None

    def test_household_with_admin_areas(self) -> None:
        household_data = {
            "country": "AF",
            "country_origin": "AF",
            "size": 2,
            "consent_sharing": ["UNICEF"],
            "village": "Test Village",
            "head_of_household": self.head_of_household.unicef_id,
            "primary_collector": self.primary_collector.unicef_id,
            "alternate_collector": self.alternate_collector.unicef_id,
            "members": [self.head_of_household.unicef_id, self.primary_collector.unicef_id],
            "admin1": self.admin1.p_code,
            "admin2": self.admin2.p_code,
            "admin3": self.admin3.p_code,
            "admin4": self.admin4.p_code,
        }

        response = self.client.post(self.url, [household_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 0

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        assert household.admin1 == self.admin1
        assert household.admin2 == self.admin2
        assert household.admin3 == self.admin3
        assert household.admin4 == self.admin4

    def test_create_household_with_consent_sign(self) -> None:
        household_data = {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
            "consent_sign": self.base64_encoded_data,
            "village": "Test Village",
            "head_of_household": self.head_of_household.unicef_id,
            "primary_collector": self.primary_collector.unicef_id,
            "members": [
                self.head_of_household.unicef_id,
                self.primary_collector.unicef_id,
            ],
        }

        response = self.client.post(self.url, [household_data], format="json")

        assert response.status_code == status.HTTP_201_CREATED, str(response.json())
        assert response.data["processed"] == 1
        assert response.data["accepted"] == 1
        assert response.data["errors"] == 0

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        assert household.consent_sign is not None
        assert household.consent_sign.name.startswith(self.program.programme_code)
        assert household.consent_sign.name.endswith(".png")

    def test_consent_sign_cleanup_on_failure(self) -> None:
        household_data = {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF", "PRIVATE_PARTNER"],
            "consent_sign": self.base64_encoded_data,
            "village": "Test Village",
            "head_of_household": self.head_of_household.unicef_id,
            "primary_collector": self.primary_collector.unicef_id,
            "members": [
                self.head_of_household.unicef_id,
                self.primary_collector.unicef_id,
            ],
        }

        with tempfile.TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):

                def fail_after_files_exist(*args, **kwargs):
                    pre_cleanup_files = []
                    for root, _, files in os.walk(media_root):
                        pre_cleanup_files.extend(os.path.join(root, f) for f in files)
                    assert len(pre_cleanup_files) > 0
                    raise RuntimeError("forced failure for consent sign cleanup test")

                with patch(
                    "hope.api.endpoints.rdi.lax.PendingHousehold.objects.bulk_create",
                    side_effect=fail_after_files_exist,
                ):
                    with pytest.raises(RuntimeError):
                        self.client.post(self.url, [household_data], format="json")

                leftover_files = []
                for root, _, files in os.walk(media_root):
                    leftover_files.extend(os.path.join(root, f) for f in files)
                assert leftover_files == []


pytestmark = pytest.mark.django_db


@pytest.fixture
def household_base64_image() -> str:
    image = Path(__file__).parent / "logo.png"
    return base64.b64encode(image.read_bytes()).decode("utf-8")


@pytest.fixture
def household_image_flex_attribute(db: Any) -> FlexibleAttribute:
    return FlexibleAttributeFactory(
        name="household_photo_h_f",
        label={"English(EN)": "Household Photo"},
        type=FlexibleAttribute.IMAGE,
        associated_with=FlexibleAttribute.ASSOCIATED_WITH_HOUSEHOLD,
    )


@pytest.fixture
def household_api_context(
    api_client: Any,
    household_image_flex_attribute: FlexibleAttribute,
    household_base64_image: str,
) -> dict[str, Any]:
    from extras.test_utils.factories import (
        BusinessAreaFactory,
        RoleAssignmentFactory,
        RoleFactory,
        UserFactory,
    )

    business_area = BusinessAreaFactory(slug="afghanistan")
    country = CountryFactory(
        name="Afghanistan", short_name="Afghanistan", iso_code2="AF", iso_code3="AFG", iso_num="0004"
    )

    admin_type_1 = AreaTypeFactory(country=country, area_level=1)
    AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)

    program = ProgramFactory(status=Program.DRAFT, business_area=business_area)
    rdi = RegistrationDataImportFactory(
        business_area=business_area,
        number_of_individuals=0,
        number_of_households=0,
        status=RegistrationDataImport.LOADING,
        program=program,
    )

    head_of_household = PendingIndividualFactory(
        individual_id="IND001",
        registration_data_import=rdi,
        program=program,
        business_area=business_area,
    )
    primary_collector = PendingIndividualFactory(
        individual_id="IND002",
        registration_data_import=rdi,
        program=program,
        business_area=business_area,
    )

    user = UserFactory()
    role = RoleFactory(name="API Role", subsystem="API", permissions=[Grant.API_RDI_CREATE.name])
    RoleAssignmentFactory(user=user, role=role, business_area=business_area)
    token = APITokenFactory(
        user=user,
        grants=[Grant.API_RDI_CREATE.name],
    )
    token.valid_for.set([business_area])
    client = api_client(user)
    url = reverse("api:rdi-push-lax-households", args=[business_area.slug, str(rdi.id)])

    return {
        "client": client,
        "url": url,
        "base64_image": household_base64_image,
        "program": program,
        "business_area": business_area,
        "head_of_household": head_of_household,
        "primary_collector": primary_collector,
        "household_data": {
            "country": "AF",
            "country_origin": "AF",
            "size": 1,
            "consent_sharing": ["UNICEF"],
            "village": "Test Village",
            "head_of_household": head_of_household.unicef_id,
            "primary_collector": primary_collector.unicef_id,
            "members": [head_of_household.unicef_id],
            "household_photo": household_base64_image,
        },
    }


def test_household_with_image_flex_field(household_api_context: dict[str, Any]) -> None:
    ctx = household_api_context
    response = ctx["client"].post(ctx["url"], [ctx["household_data"]], format="json")

    assert response.status_code == status.HTTP_201_CREATED, str(response.json())
    assert response.data["accepted"] == 1

    household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
    assert "household_photo" in household.flex_fields
    assert not household.flex_fields["household_photo"].startswith(ctx["base64_image"][:20])
    assert default_storage.exists(household.flex_fields["household_photo"])


def test_household_image_flex_field_cleanup_on_failure(household_api_context: dict[str, Any]) -> None:
    ctx = household_api_context

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
                with pytest.raises(RuntimeError):
                    ctx["client"].post(ctx["url"], [ctx["household_data"]], format="json")

            leftover_files = []
            for root, _, files in os.walk(media_root):
                leftover_files.extend(os.path.join(root, f) for f in files)
            assert leftover_files == []
