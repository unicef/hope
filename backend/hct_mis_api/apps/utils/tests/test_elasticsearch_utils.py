from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase, APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    HouseholdFactory,
    IndividualFactory,
    DocumentTypeFactory,
    DocumentFactory
)
from hct_mis_api.apps.household.models import DocumentType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import bulk_upsert_households, bulk_upsert_individuals


class TestBulkUpsert(BaseElasticSearchTestCase, APITestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = UserFactory()
        cls.business_area = create_afghanistan()
        cls.program = ProgramFactory(
            name="JustProgram",
            business_area=cls.business_area,
            status=Program.ACTIVE,
        )

        DocumentTypeFactory(key="national_id")
        DocumentTypeFactory(key="national_passport")

        # this goes to es
        cls.household_1 = HouseholdFactory.build(business_area=cls.business_area)
        cls.individual_1 = IndividualFactory()

        DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=cls.individual_1,
        )

        cls.household_1.head_of_household = cls.individual_1
        cls.household_1.admin1 = "just_admin"
        cls.household_1.admin2 = "wow_admin"
        cls.household_1.registration_id = "12345"
        cls.household_1.save()

        cls.rebuild_search_index()

        # This goes to postgres
        cls.household_2 = HouseholdFactory.build(business_area=cls.business_area)
        cls.individual_2 = IndividualFactory()

        DocumentFactory(
            document_number="987-654-321",
            type=DocumentType.objects.get(key="national_passport"),
            individual=cls.individual_2,
        )

        cls.household_2.head_of_household = cls.individual_2
        cls.household_2.admin1 = "some_admin"
        cls.household_2.admin2 = "other_admin"
        cls.household_2.registration_id = "54321"
        cls.household_2.save()

    def test_bulk_upsert_household(self) -> None:
        bulk_upsert_households([])

        # do something

    def test_bulk_upsert_individuals(self) -> None:
        bulk_upsert_individuals([])

        # do something
