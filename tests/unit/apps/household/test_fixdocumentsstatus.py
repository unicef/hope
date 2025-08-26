from django.core.management import call_command
from django.test import TestCase
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.household import (
    DocumentFactory,
    create_household_for_fixtures,
)

from hope.apps.household.management.commands.fixdocumentsstatus import (
    fix_documents_statuses,
)
from hope.models.household import Document, Household, Individual


class TestDocumentStatusFixer(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("generatedocumenttypes")

    def test_fix_status(self) -> None:
        _, individuals = create_household_for_fixtures({"size": 5})
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        household, individuals = create_household_for_fixtures({"size": 5, "withdrawn": True}, {"withdrawn": True})
        for individual in individuals:
            DocumentFactory.create_batch(2, individual=individual, status=Document.STATUS_VALID)
            DocumentFactory.create_batch(3, individual=individual, status=Document.STATUS_NEED_INVESTIGATION)

        fixed_documents = fix_documents_statuses()

        assert Household.objects.filter(withdrawn=True).count(), 1
        assert Individual.objects.filter(withdrawn=True).count() == 5
        assert Document.objects.filter(status=Document.STATUS_NEED_INVESTIGATION).count() == 40
        assert fixed_documents == 10
