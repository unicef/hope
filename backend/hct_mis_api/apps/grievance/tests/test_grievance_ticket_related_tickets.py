from django.core.management import call_command

from django_countries.fields import Country

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import AdminAreaFactory, AdminAreaLevelFactory
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    DocumentType,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestGrievanceTicketRelatedTickets(APITestCase):
    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.generate_document_types_for_all_countries()
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=self.business_area,
        )
        AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="test334")
        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        individual_data = {
            "full_name": "Benjamin Butler",
            "given_name": "Benjamin",
            "family_name": "Butler",
            "phone_no": "(953)682-4596",
            "birth_date": "1943-07-30",
            "household": household_one,
        }

        individual = IndividualFactory(**individual_data)
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )

        DocumentFactory(
            id="df1ce6e8-2864-4c3f-803d-19ec6f4c47f3",
            type=national_id_type,
            document_number="789-789-645",
            individual=individual,
        )
        DocumentFactory(
            id="8ad5e3b8-4c4d-4c10-8756-118d86095dd0",
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=individual,
        )
        household_one.head_of_household = individual
        household_one.save()

        self.grievance_tickets = GrievanceTicketFactory.create_batch(5)

    def test_should_return_distinct_related_tickets(self):
        ticket1 = GrievanceTicketFactory.create()
        ticket2 = GrievanceTicketFactory.create()

        ticket1.linked_tickets.set(self.grievance_tickets)
        ticket2.linked_tickets.set([ticket for ticket in self.grievance_tickets] + [ticket1])

        ticket1_related_tickets_count = len([ticket for ticket in ticket1.related_tickets])
        ticket2_related_tickets_count = len([ticket for ticket in ticket2.related_tickets])
        self.assertEqual(ticket1_related_tickets_count, 6)
        self.assertEqual(ticket2_related_tickets_count, 6)
