import time

from django.conf import settings

from elasticsearch import Elasticsearch

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase, BaseElasticSearchTestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.geo.fixtures import AreaFactory
from hct_mis_api.apps.household.documents import (
    HouseholdDocument,
    IndividualDocumentAfghanistan,
)
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import DocumentType, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_bulk_upsert import (
    bulk_upsert_households,
    bulk_upsert_individuals,
)


class TestBulkUpsert(BaseElasticSearchTestCase, APITestCase):
    databases = {"default", "registration_datahub"}

    es = Elasticsearch(settings.ELASTICSEARCH_HOST)

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
        cls.household_1.registration_data_import.imported_by.save()
        cls.household_1.registration_data_import.save()

        cls.individual_1 = IndividualFactory(household=cls.household_1)

        DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=cls.individual_1,
        )

        cls.household_1.head_of_household = cls.individual_1
        cls.household_1.admin1 = AreaFactory()
        cls.household_1.admin2 = AreaFactory()
        cls.household_1.registration_id = "12345"
        cls.household_1.household_collection.save()
        cls.household_1.save()

        cls.rebuild_search_index()

        # This goes to postgres and is not in es
        cls.household_2 = HouseholdFactory.build(business_area=cls.business_area)
        cls.household_2.registration_data_import.imported_by.save()
        cls.household_2.registration_data_import.save()

        cls.individual_2 = IndividualFactory(household=cls.household_2)

        DocumentFactory(
            document_number="987-654-321",
            type=DocumentType.objects.get(key="national_passport"),
            individual=cls.individual_2,
        )

        cls.household_2.head_of_household = cls.individual_2
        cls.household_2.admin1 = AreaFactory()
        cls.household_2.admin2 = AreaFactory()
        cls.household_2.registration_id = "54321"
        cls.household_2.household_collection.save()
        cls.household_2.save()

        cls.household_unicef_id_to_search = Individual.objects.get(
            full_name=cls.individual_2.full_name
        ).household.unicef_id
        cls.individual_unicef_id_to_search = Individual.objects.get(full_name=cls.individual_2.full_name).unicef_id

    def test_bulk_upsert_household(self) -> None:
        _id = self.household_unicef_id_to_search
        bulk_upsert_households([_id])
        time.sleep(1)
        es_response = (
            HouseholdDocument()
            .search()
            .from_dict({"query": {"bool": {"should": [{"match_phrase_prefix": {"unicef_id": _id}}]}}})
            .execute()
        )
        item = es_response.to_dict()["hits"]["hits"][0]["_source"]
        self.assertEqual(item["business_area"], self.household_2.business_area.slug)
        self.assertEqual(item["registration_id"], int(self.household_2.registration_id))
        self.assertEqual(item["unicef_id"], self.household_unicef_id_to_search)
        self.assertEqual(item["head_of_household"]["full_name"], self.individual_2.full_name)

    def test_bulk_upsert_individuals(self) -> None:
        _id = self.individual_unicef_id_to_search
        bulk_upsert_individuals([_id])
        time.sleep(1)
        es_response = (
            IndividualDocumentAfghanistan()
            .search()
            .from_dict({"query": {"bool": {"should": [{"match_phrase_prefix": {"unicef_id": _id}}]}}})
            .execute()
        )
        item = es_response.to_dict()["hits"]["hits"][0]["_source"]
        self.assertEqual(item["full_name"], self.individual_2.full_name)
        self.assertEqual(item["birth_date"], str(self.individual_2.birth_date))
        self.assertEqual(item["phone_no"], self.individual_2.phone_no)
        self.assertEqual(item["business_area"], self.individual_2.business_area.slug)
        self.assertEqual(item["unicef_id"], self.individual_unicef_id_to_search)
        self.assertEqual(item["documents"][0]["number"], "987-654-321")
        self.assertEqual(item["relationship"], self.individual_2.relationship)
        self.assertEqual(item["sex"], self.individual_2.sex)
