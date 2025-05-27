from datetime import datetime

from django.conf import settings
from django.test import TestCase
from django.utils import timezone

import pytest

from hct_mis_api.apps.sanction_list.models import SanctionListIndividual
from hct_mis_api.apps.sanction_list.tasks.load_xml import LoadSanctionListXMLTask

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestLoadXML(TestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    def test_execute(self) -> None:
        main_test_files_path = f"{settings.TESTS_ROOT}/apps/sanction_list/test_files"

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/original-consolidated.xml")
        task.execute()

        individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(individuals.count(), 1)

        kpi_33_documents = individuals.get(reference_number="KPi.111").documents.all()
        self.assertEqual(kpi_33_documents.count(), 1)

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/updated-consolidated.xml")
        task.execute()

        all_individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(all_individuals.count(), 1)

        active_individuals = SanctionListIndividual.objects.filter(active=True)
        self.assertEqual(active_individuals.count(), 1)

        updated_individual = active_individuals.get(reference_number="KPi.111")
        self.assertEqual(updated_individual.third_name, "TEST")
        self.assertEqual(updated_individual.listed_on, timezone.make_aware(datetime(year=2016, month=11, day=11)))

        self.assertEqual(updated_individual.documents.all().count(), 2)

        test_doc = updated_individual.documents.get(document_number="111222333555")
        self.assertEqual(test_doc.type_of_document, "Passport")

        task = LoadSanctionListXMLTask(file_path=f"{main_test_files_path}/updated2-consolidated.xml")
        task.execute()

        all_individuals = SanctionListIndividual.all_objects.all()
        self.assertEqual(all_individuals.count(), 1)

        active_individuals = SanctionListIndividual.objects.filter(active=True)
        self.assertEqual(active_individuals.count(), 1)

        updated_individual = active_individuals.get(reference_number="KPi.111")
        self.assertEqual(updated_individual.listed_on, timezone.make_aware(datetime(year=2016, month=11, day=11)))
