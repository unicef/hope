from django.core.exceptions import ValidationError
from django.test import TestCase

import pytest

from hct_mis_api.apps.account.fixtures import BusinessAreaFactory, UserFactory
from hct_mis_api.apps.core.utils import encode_id_base64
from hct_mis_api.apps.geo.fixtures import AreaFactory, CountryFactory
from hct_mis_api.apps.geo.models import Country
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
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestUpdateIndividualDataService(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.business_area = BusinessAreaFactory()
        cls.program = ProgramFactory()
        cls.country_afg = CountryFactory(iso_code3="AFG")
        cls.user = UserFactory()

        cls.household, _ = create_household({"program": cls.program})

        cls.individual = IndividualFactory(
            household=cls.household, business_area=cls.business_area, program=cls.program
        )

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
        rebuild_search_index()

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
            service.close(self.user)
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
            service.close(self.user)
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
            service.close(self.user)
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
            service.close(self.user)
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
            service.close(self.user)
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
            service.close(self.user)
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
            service.close(self.user)
        self.assertEqual(
            f"Document with number {existing_document.document_number} of type {self.document_type_unique_for_individual} already exists",
            e.exception.message,
        )

        document_to_edit.refresh_from_db()
        # document was not updated
        self.assertEqual(document_to_edit.document_number, "111111")

    def test_update_people_individual_hh_fields(self) -> None:
        pl = CountryFactory(name="Poland", iso_code3="POL", iso_code2="PL", iso_num="620")
        CountryFactory(name="Other Country", short_name="Oth", iso_code2="O", iso_code3="OTH", iso_num="111")
        AreaFactory(area_type__country=pl, p_code="PL22M33", name="Test Area M")
        hh_fields = [
            "consent",
            "residence_status",
            "country_origin",
            "country",
            "address",
            "village",
            "currency",
            "unhcr_id",
            "name_enumerator",
            "org_enumerator",
            "org_name_enumerator",
            "registration_method",
        ]
        hh = self.household
        ind_data = {}
        new_data = {
            "address": "Test Address ABC",
            "country_origin": "POL",
            "country": "OTH",
            "residence_status": "HOST",
            "village": "El Paso",
            "consent": None,
            "currency": "PLN",
            "unhcr_id": "random_unhcr_id_123",
            "name_enumerator": "test_name",
            "org_enumerator": "test_org",
            "org_name_enumerator": "test_org_name",
            "registration_method": "COMMUNITY",
        }
        for hh_field in hh_fields:
            ind_data[hh_field] = {
                "value": new_data.get(hh_field),
                "approve_status": True,
                "previous_value": (
                    getattr(hh, hh_field).iso_code3
                    if isinstance(getattr(hh, hh_field), Country)
                    else getattr(hh, hh_field)
                ),
            }
        # add admin_area_title > HH.admin_area
        ind_data["admin_area_title"] = {"value": "PL22M33", "approve_status": True, "previous_value": None}
        self.ticket.individual_data_update_ticket_details.individual_data = ind_data
        self.ticket.individual_data_update_ticket_details.save()

        service = IndividualDataUpdateService(self.ticket, self.ticket.individual_data_update_ticket_details)
        service.close(self.user)

        hh.refresh_from_db()
        for hh_field in hh_fields:
            hh_value = (
                getattr(hh, hh_field).iso_code3 if isinstance(getattr(hh, hh_field), Country) else getattr(hh, hh_field)
            )
            self.assertEqual(hh_value, new_data.get(hh_field))

        self.assertEqual(hh.admin_area.p_code, "PL22M33")
        self.assertEqual(hh.admin_area.name, "Test Area M")
