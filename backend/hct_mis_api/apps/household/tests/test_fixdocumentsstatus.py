from django.test import TestCase

from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    create_household_for_fixtures,
)
from hct_mis_api.apps.household.management.commands.fixdocumentsstatus import (
    fix_documents_statuses,
)
from hct_mis_api.apps.household.models import Document, Household, Individual


class TestDocumentStatusFixer(TestCase):
    def test_fix_status(self):
        create_afghanistan()

        _, individuals = create_household_for_fixtures({"size": 5})
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        household, individuals = create_household_for_fixtures({"size": 5, "withdrawn": True}, {"withdrawn": True})
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        fixed_documents = fix_documents_statuses()

        self.assertTrue(Household.objects.filter(withdrawn=True).count(), 1)
        self.assertEqual(Individual.objects.filter(withdrawn=True).count(), 5)
        self.assertEqual(Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count(), 40)
        self.assertEqual(fixed_documents, 10)
