from django.core.management import call_command

from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import PendingIndividualFactory
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework import status
from rest_framework.reverse import reverse
from unit.api.base import HOPEApiTestCase

from hct_mis_api.api.models import Grant
from hct_mis_api.apps.household.models import PendingHousehold
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.models import RegistrationDataImport


class CreateLaxHouseholdsTests(HOPEApiTestCase):
    databases = {"default"}
    user_permissions = [Grant.API_RDI_CREATE]

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        call_command("loadcountries")
        call_command("loadcountrycodes")

        cls.program = ProgramFactory(status=Program.DRAFT, business_area=cls.business_area)

        cls.rdi: RegistrationDataImport = RegistrationDataImportFactory(
            business_area=cls.business_area,
            number_of_individuals=0,
            number_of_households=0,
            status=RegistrationDataImport.LOADING,
            program=cls.program,
        )

        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        admin_type_3 = AreaTypeFactory(country=country, area_level=3, parent=admin_type_2)
        admin_type_4 = AreaTypeFactory(country=country, area_level=4, parent=admin_type_3)

        cls.admin1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        cls.admin2 = AreaFactory(parent=cls.admin1, p_code="AF0101", area_type=admin_type_2)
        cls.admin3 = AreaFactory(parent=cls.admin2, p_code="AF010101", area_type=admin_type_3)
        cls.admin4 = AreaFactory(parent=cls.admin3, p_code="AF01010101", area_type=admin_type_4)

        cls.url = reverse("api:rdi-push-lax-households", args=[cls.business_area.slug, str(cls.rdi.id)])

    def setUp(self) -> None:
        super().setUp()
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 0)

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        self.assertEqual(household.country.iso_code2, "AF")
        self.assertEqual(household.country_origin.iso_code2, "AF")
        self.assertEqual(household.size, 3)
        self.assertEqual(sorted(household.consent_sharing), sorted(["UNICEF", "PRIVATE_PARTNER"]))
        self.assertEqual(household.village, "Test Village")
        self.assertEqual(household.head_of_household, self.head_of_household)
        self.assertEqual(household.primary_collector, self.primary_collector)
        self.assertEqual(household.alternate_collector, self.alternate_collector)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 2)
        self.assertEqual(response.data["accepted"], 2)
        self.assertEqual(response.data["errors"], 0)

    def test_create_household_with_validation_errors(self) -> None:
        household_data = {
            "country": "INVALID_COUNTRY",
            "size": -1,
            "head_of_household": "NON_EXISTENT_ID",
            "primary_collector": "NON_EXISTENT_ID",
            "members": [],
        }

        response = self.client.post(self.url, [household_data], format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 0)
        self.assertEqual(response.data["errors"], 1)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 2)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 1)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 0)

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        self.assertEqual(household.alternate_collector, None)

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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, str(response.json()))
        self.assertEqual(response.data["processed"], 1)
        self.assertEqual(response.data["accepted"], 1)
        self.assertEqual(response.data["errors"], 0)

        household = PendingHousehold.objects.get(id=response.data["results"][0]["pk"])
        self.assertEqual(household.admin1, self.admin1)
        self.assertEqual(household.admin2, self.admin2)
        self.assertEqual(household.admin3, self.admin3)
        self.assertEqual(household.admin4, self.admin4)
