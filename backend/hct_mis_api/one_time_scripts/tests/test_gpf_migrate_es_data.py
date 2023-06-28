import logging
from contextlib import contextmanager
from typing import Dict, Iterator, List

from django.test import TestCase

from elasticsearch import Elasticsearch

from hct_mis_api.apps.core.fixtures import (
    create_afghanistan,
    create_kenya,
    create_ukraine,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.household.documents import (
    HouseholdDocument,
    IndividualDocumentAfghanistan,
    IndividualDocumentOthers,
    IndividualDocumentUkraine,
)
from hct_mis_api.apps.household.fixtures import HouseholdFactory, IndividualFactory
from hct_mis_api.apps.household.models import Household, Individual
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.utils.elasticsearch_utils import _populate, delete_all_indexes
from hct_mis_api.one_time_scripts.gpf_migrate_es_data import migrate_program_es_db


@contextmanager
def use_es() -> Iterator[None]:
    _populate(models=[Household, Individual], options={"parallel": False, "quiet": True})
    try:
        yield
    except Exception as e:
        print(f"Exception raised: {e}")
    finally:
        delete_all_indexes()


def create_query(obj_list: List[str]) -> Dict:
    return {"query": {"terms": {"_id": obj_list}}}


class TestGPFMigrationToES(TestCase):
    databases = {"default"}

    @classmethod
    def setUpTestData(cls) -> None:
        create_afghanistan()
        create_ukraine()
        create_kenya()  # kenya is in others index

        cls.ukraine_ba = BusinessArea.objects.get(slug="ukraine")
        cls.afghanistan_ba = BusinessArea.objects.get(slug="afghanistan")
        cls.kenya_ba = BusinessArea.objects.get(slug="kenya")

        cls.program_1 = ProgramFactory(business_area=cls.ukraine_ba)
        cls.program_2 = ProgramFactory(business_area=cls.ukraine_ba)
        cls.program_3 = ProgramFactory(business_area=cls.afghanistan_ba)
        cls.program_4 = ProgramFactory(business_area=cls.kenya_ba)

        cls.individual_1 = IndividualFactory(household=None, program=cls.program_1, business_area=cls.ukraine_ba)
        cls.household_1 = HouseholdFactory(
            head_of_household=cls.individual_1, program=cls.program_1, business_area=cls.ukraine_ba
        )

        cls.individual_2 = IndividualFactory(household=None, program=cls.program_2, business_area=cls.ukraine_ba)
        cls.household_2 = HouseholdFactory(
            head_of_household=cls.individual_2, program=cls.program_2, business_area=cls.ukraine_ba
        )

        cls.individual_3 = IndividualFactory(household=None, program=cls.program_3, business_area=cls.afghanistan_ba)
        cls.household_3 = HouseholdFactory(
            head_of_household=cls.individual_3, program=cls.program_3, business_area=cls.afghanistan_ba
        )

        cls.individual_4 = IndividualFactory(household=None, program=cls.program_4, business_area=cls.kenya_ba)
        cls.household_4 = HouseholdFactory(
            head_of_household=cls.individual_4, program=cls.program_4, business_area=cls.kenya_ba
        )

    def test_migrate_program_id_to_household_es(self) -> None:
        logging.disable(logging.INFO)
        logging.disable(logging.ERROR)

        with use_es():
            migrate_program_es_db()

            query_dict = create_query([self.household_1.id, self.household_2.id, self.household_3.id])

            es = Elasticsearch("elasticsearch")
            es.indices.refresh(index=HouseholdDocument.Index.name)
            results = es.search(index=HouseholdDocument.Index.name, body=query_dict)
            hits = results["hits"]["hits"]

            self.assertEqual(hits[0]["_source"]["program_id"], str(self.program_1.id))
            self.assertEqual(hits[1]["_source"]["program_id"], str(self.program_2.id))
            self.assertEqual(hits[2]["_source"]["program_id"], str(self.program_3.id))

    def test_migrate_program_id_to_individual_es(self) -> None:
        logging.disable(logging.INFO)
        logging.disable(logging.ERROR)

        with use_es():
            migrate_program_es_db()

            es = Elasticsearch("elasticsearch")

            es.indices.refresh(index=IndividualDocumentAfghanistan.Index.name)
            es.indices.refresh(index=IndividualDocumentUkraine.Index.name)
            es.indices.refresh(index=IndividualDocumentOthers.Index.name)

            query_dict = create_query([self.individual_3.id])
            results = es.search(index=IndividualDocumentAfghanistan.Index.name, body=query_dict)
            hits = results["hits"]["hits"]

            self.assertEqual(hits[0]["_source"]["program_id"], str(self.program_3.id))

            query_dict = create_query([self.individual_1.id, self.individual_2.id])
            results = es.search(index=IndividualDocumentUkraine.Index.name, body=query_dict)
            hits = results["hits"]["hits"]

            self.assertEqual(hits[0]["_source"]["program_id"], str(self.program_1.id))
            self.assertEqual(hits[1]["_source"]["program_id"], str(self.program_2.id))

            query_dict = create_query([self.individual_4.id])
            results = es.search(index=IndividualDocumentOthers.Index.name, body=query_dict)
            hits = results["hits"]["hits"]

            self.assertEqual(hits[0]["_source"]["program_id"], str(self.program_4.id))
