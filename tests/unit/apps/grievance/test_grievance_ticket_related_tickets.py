from django.core.management import call_command

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
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
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="test334")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(program=program_one)
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = program_one
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        individual_data = {
            "full_name": "Benjamin Butler",
            "given_name": "Benjamin",
            "family_name": "Butler",
            "phone_no": "(953)682-4596",
            "birth_date": "1943-07-30",
            "household": household_one,
            "program": program_one,
        }

        individual = IndividualFactory(**individual_data)
        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        birth_certificate_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )

        DocumentFactory(
            id="df1ce6e8-2864-4c3f-803d-19ec6f4c47f3",
            country=country_pl,
            type=national_id_type,
            document_number="789-789-645",
            individual=individual,
            program=individual.program,
        )
        DocumentFactory(
            id="8ad5e3b8-4c4d-4c10-8756-118d86095dd0",
            country=country_pl,
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=individual,
            program=individual.program,
        )
        household_one.head_of_household = individual
        household_one.save()

        cls.grievance_tickets = GrievanceTicketFactory.create_batch(5)

    def test_should_return_distinct_related_tickets(self) -> None:
        ticket1 = GrievanceTicketFactory.create()
        ticket2 = GrievanceTicketFactory.create()

        ticket1.linked_tickets.set(self.grievance_tickets)
        ticket2.linked_tickets.set(list(self.grievance_tickets) + [ticket1])

        self.assertEqual(ticket1.linked_tickets.count(), 6)
        self.assertEqual(ticket2.linked_tickets.count(), 6)
