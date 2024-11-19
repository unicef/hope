from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

import pytest

from hct_mis_api.apps.sanction_list.models import SanctionListIndividual
from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


class TestLoadXML(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    def test_execute(self) -> None:
        main_test_files_path = f"{settings.TESTS_ROOT}/apps/sanction_list/test_files"

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/original-consolidated.xml")
        task.execute()

        individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(individuals.count(), 3)

        kpi_33_documents = individuals.get(reference_number="KPi.033").documents.all()
        self.assertEqual(kpi_33_documents.count(), 1)

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/updated-consolidated.xml")
        task.execute()

        all_individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(all_individuals.count(), 3)

        active_individuals = SanctionListIndividual.objects.filter(active=True)
        self.assertEqual(active_individuals.count(), 2)

        updated_individual = active_individuals.get(reference_number="KPi.033")
        self.assertEqual(updated_individual.third_name, "TEST")
        self.assertEqual(updated_individual.listed_on, timezone.make_aware(datetime(year=2020, month=11, day=30)))

        self.assertEqual(updated_individual.documents.all().count(), 2)

        test_doc = updated_individual.documents.get(document_number="1233214321")
        self.assertEqual(test_doc.type_of_document, "Test Doc Type")

        self.assertIn(
            "KP",
            updated_individual.nationalities.values_list("nationality__iso_code2", flat=True),
        )

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/updated2-consolidated.xml")
        task.execute()

        all_individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(all_individuals.count(), 3)

        active_individuals = SanctionListIndividual.objects.filter(active=True)
        self.assertEqual(active_individuals.count(), 3)

        updated_individual = active_individuals.get(reference_number="KPi.037")
        self.assertEqual(updated_individual.listed_on, timezone.make_aware(datetime(year=2020, month=11, day=30)))
