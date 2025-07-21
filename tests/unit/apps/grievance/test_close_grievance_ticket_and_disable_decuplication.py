from datetime import date
from unittest import mock

from django.conf import settings

import pytest

from tests.extras.test_utils.factories.account import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from tests.extras.test_utils.factories.core import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from tests.extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from tests.extras.test_utils.factories.grievance import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from tests.extras.test_utils.factories.household import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    RELATIONSHIP_UNKNOWN,
    ROLE_PRIMARY,
    SINGLE,
    UNIQUE_IN_BATCH,
    DocumentType,
)
from tests.extras.test_utils.factories.fixtures import ProgramFactory
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
class TestCloseGrievanceTicketAndDisableDeduplication(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

    UPDATE_GRIEVANCE_TICKET_STATUS_CHANGE_MUTATION = """
    mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
        grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
            grievanceTicket {
                id
                status
            }
        }
    }
    """

    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory(id="a5c44eeb-482e-49c2-b5ab-d769f83db116")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")
        cls.business_area.postpone_deduplication = True
        cls.business_area.save()

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123333")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="2343123")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(size=2, village="Example", program=program_one)
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = program_one
        household_one.registration_data_import.save()
        household_one.program = program_one

        cls.individual = IndividualFactory(household=household_one, program=program_one)
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        birth_certificate_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )
        cls.national_id = DocumentFactory(
            type=national_id_type,
            document_number="789-789-645",
            individual=cls.individual,
            country=country,
            program=program_one,
        )
        cls.birth_certificate = DocumentFactory(
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=cls.individual,
            country=country,
            program=program_one,
        )
        household_one.head_of_household = cls.individual
        household_one.save()
        cls.household_one = household_one
        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=cls.admin_area_1,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=cls.user,
        )
        cls.add_individual_grievance_ticket.programs.add(program_one)
        TicketAddIndividualDetailsFactory(
            ticket=cls.add_individual_grievance_ticket,
            household=cls.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "relationship": RELATIONSHIP_UNKNOWN,
                "estimated_birth_date": False,
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "role": ROLE_PRIMARY,
                "documents": [
                    {
                        "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                        "country": "POL",
                        "number": "123-123-UX-321",
                    }
                ],
            },
            approve_status=True,
        )
        rebuild_search_index()

    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_add_individual_close_ticket_for_postponed_deduplication(self) -> None:
        permissions = [
            Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK,
        ]
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )

        self.assertFalse("errors" in response)
        self.assertTrue("data" in response)
        self.assertEqual(
            response["data"]["grievanceStatusChange"]["grievanceTicket"]["status"], GrievanceTicket.STATUS_CLOSED
        )

        self.individual.refresh_from_db()
        self.assertEqual(self.individual.deduplication_batch_status, UNIQUE_IN_BATCH)
        self.assertEqual(self.individual.deduplication_golden_record_results, dict())

        self.add_individual_grievance_ticket.refresh_from_db()
        self.assertEqual(self.add_individual_grievance_ticket.status, GrievanceTicket.STATUS_CLOSED)
