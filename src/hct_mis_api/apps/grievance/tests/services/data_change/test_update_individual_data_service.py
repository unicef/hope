from django.core.exceptions import ValidationError
from django.test import TestCase

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.base_test_case import BaseElasticSearchTestCase
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo.fixtures import CountryFactory
from hct_mis_api.apps.grievance.fixtures import TicketIndividualDataUpdateDetailsFactory
from hct_mis_api.apps.grievance.services.data_change.individual_data_update_service import (
    IndividualDataUpdateService,
)
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    DocumentTypeFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import Document
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestUpdateIndividualDataService(BaseElasticSearchTestCase, TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.business_area = BusinessAreaFactory()
        cls.program = ProgramFactory()
        cls.country_afg = CountryFactory(iso_code3="AFG")

        household, _ = create_household({"program": cls.program})

        cls.individual = IndividualFactory(household=household, business_area=cls.business_area, program=cls.program)

        cls.document_type_unique_for_individual = DocumentTypeFactory(
            unique_for_individual=True, key="unique", label="Unique"
        )
        cls.document_type_unique_for_individual.refresh_from_db()
        cls.document_type_not_unique_for_individual = DocumentTypeFactory(
            unique_for_individual=False, key="not_unique", label="Not unique"
        )

        ticket_details = TicketIndividualDataUpdateDetailsFactory(
            individual=cls.individual,
            individual_data={
                "documents": [],
            },
        )

        cls.ticket = ticket_details.ticket
        cls.ticket.save()
        super().setUpTestData()

    def test_add_document_of_same_type_not_unique_per_individual_valid(self) -> None:
        DocumentFactory(
            individual=self.individual,
            type=self.document_type_not_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents"] = [
            {
                "value": {
                    "key": self.document_type_not_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)

        try:
            service.close(UserFactory())
        except ValidationError:
            self.fail("ValidationError should not be raised")

        self.assertEqual(Document.objects.filter(document_number="111111").count(), 1)

    def test_add_document_of_same_type_not_unique_per_individual_pending(self) -> None:
        DocumentFactory(
            individual=self.individual,
            type=self.document_type_not_unique_for_individual,
            status=Document.STATUS_PENDING,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents"] = [
            {
                "value": {
                    "key": self.document_type_not_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        try:
            service.close(UserFactory())
        except ValidationError:
            self.fail("ValidationError should not be raised")

        self.assertEqual(Document.objects.filter(document_number="111111").count(), 1)

    def test_add_document_of_same_type_unique_per_individual_valid(self) -> None:
        DocumentFactory(
            individual=self.individual,
            type=self.document_type_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents"] = [
            {
                "value": {
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        with self.assertRaises(ValidationError) as e:
            service.close(UserFactory())
        self.assertEqual(
            f"Document of type {self.document_type_unique_for_individual} already exists for this individual",
            e.exception.message,
        )

        self.assertEqual(Document.objects.filter(document_number="111111").count(), 0)

    def test_add_document_of_same_type_unique_per_individual_pending(self) -> None:
        DocumentFactory(
            individual=self.individual,
            type=self.document_type_unique_for_individual,
            status=Document.STATUS_PENDING,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents"] = [
            {
                "value": {
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        try:
            service.close(UserFactory())
        except ValidationError:
            self.fail("ValidationError should not be raised")

        self.assertEqual(Document.objects.filter(document_number="111111").count(), 1)

    def test_edit_document_of_same_type_unique_per_individual(self) -> None:
        DocumentFactory(
            individual=self.individual,
            type=self.document_type_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )
        document_to_edit = DocumentFactory(
            individual=self.individual,
            type=self.document_type_not_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="111111",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
            {
                "value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "previous_value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_not_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)

        with self.assertRaises(ValidationError) as e:
            service.close(UserFactory())
        self.assertEqual(
            f"Document of type {self.document_type_unique_for_individual} already exists for this individual",
            e.exception.message,
        )

        document_to_edit.refresh_from_db()
        # document was not updated
        self.assertEqual(document_to_edit.type, self.document_type_not_unique_for_individual)

    def test_edit_document_unique_per_individual(self) -> None:
        document_to_edit = DocumentFactory(
            individual=self.individual,
            type=self.document_type_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="111111",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
            {
                "value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "22222",
                },
                "previous_value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        try:
            service.close(UserFactory())
        except ValidationError:
            self.fail("ValidationError should not be raised")

        document_to_edit.refresh_from_db()
        # document updated
        self.assertEqual(document_to_edit.document_number, "22222")

    def test_edit_document_with_data_already_existing_in_same_program(self) -> None:
        household, _ = create_household({"program": self.program})
        individual = IndividualFactory(household=household, business_area=self.business_area, program=self.program)

        existing_document = DocumentFactory(
            individual=individual,
            type=self.document_type_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="123456",
            country=self.country_afg,
        )
        document_to_edit = DocumentFactory(
            individual=self.individual,
            type=self.document_type_not_unique_for_individual,
            status=Document.STATUS_VALID,
            program=self.program,
            document_number="111111",
            country=self.country_afg,
        )

        self.ticket.individual_data_update_ticket_details.individual_data["documents_to_edit"] = [
            {
                "value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_unique_for_individual.key,
                    "country": "AFG",
                    "number": "123456",
                },
                "previous_value": {
                    "id": encode_id_base64(document_to_edit.id, "DocumentNode"),
                    "key": self.document_type_not_unique_for_individual.key,
                    "country": "AFG",
                    "number": "111111",
                },
                "approve_status": True,
            }
        ]
        self.ticket.individual_data_update_ticket_details.save()
        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        with self.assertRaises(ValidationError) as e:
            service.close(UserFactory())
        self.assertEqual(
            f"Document with number {existing_document.document_number} of type {self.document_type_unique_for_individual} already exists",
            e.exception.message,
        )

        document_to_edit.refresh_from_db()
        # document was not updated
        self.assertEqual(document_to_edit.document_number, "111111")
