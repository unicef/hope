from datetime import date

from django.core.exceptions import ValidationError
from django.test import TestCase
import pytest
from rest_framework.exceptions import ValidationError as DRFValidationError

from extras.test_utils.factories.account import UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import CountryFactory
from extras.test_utils.factories.grievance import TicketAddIndividualDetailsFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    IndividualFactory,
    create_household,
)
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.grievance.services.data_change.add_individual_service import (
    AddIndividualService,
)
from hope.apps.household.models import SINGLE, Document, Individual
from hope.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestAddIndividualService(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.program = ProgramFactory()
        household, _ = create_household({"program": cls.program})
        cls.ticket_details = TicketAddIndividualDetailsFactory(
            household=household,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "documents": [],
            },
            approve_status=True,
        )
        ticket = cls.ticket_details.ticket
        ticket.save()

        cls.household = household
        cls.ticket = ticket

        rebuild_search_index()

    def test_increase_household_size_on_close_ticket(self) -> None:
        self.household.size = 3
        self.household.save(update_fields=("size",))

        service = AddIndividualService(self.ticket, {})
        service.close(UserFactory())

        self.household.refresh_from_db()
        assert self.household.size == 4

    def test_increase_household_size_when_size_is_none_on_close_ticket(self) -> None:
        self.household.size = None
        self.household.save(update_fields=("size",))

        service = AddIndividualService(self.ticket, {})
        service.close(UserFactory())

        self.household.refresh_from_db()
        household_size = Individual.objects.filter(household=self.household).count()
        assert self.household.size == household_size

    def test_add_individual_with_document_that_already_exists(self) -> None:
        individual = IndividualFactory(program=self.program, household=self.household)
        CountryFactory(iso_code3="AFG")
        document_type = DocumentTypeFactory()
        DocumentFactory(
            status=Document.STATUS_VALID,
            program=self.program,
            type=document_type,
            document_number="123456",
            individual=individual,
        )
        self.ticket_details.individual_data["documents"] = [
            {
                "key": document_type.key,
                "country": "AFG",
                "number": "123456",
            }
        ]
        self.ticket_details.save()

        service = AddIndividualService(self.ticket, {})
        with self.assertRaises(DRFValidationError):
            service.close(UserFactory())
        assert Document.objects.filter(document_number="123456").count() == 1

    def test_add_individual_with_document_that_exists_in_pending_status(self) -> None:
        individual = IndividualFactory(program=self.program, household=self.household)
        CountryFactory(iso_code3="AFG")
        document_type = DocumentTypeFactory()
        DocumentFactory(
            status=Document.STATUS_PENDING,
            program=self.program,
            type=document_type,
            document_number="123456",
            individual=individual,
        )
        self.ticket_details.individual_data["documents"] = [
            {
                "key": document_type.key,
                "country": "AFG",
                "number": "123456",
            }
        ]
        self.ticket_details.save()

        service = AddIndividualService(self.ticket, {})
        try:
            service.close(UserFactory())
        except ValidationError:
            self.fail("ValidationError should not be raised")
        assert Document.objects.filter(document_number="123456", status=Document.STATUS_VALID).count() == 0
        assert Document.objects.filter(document_number="123456").count() == 2
