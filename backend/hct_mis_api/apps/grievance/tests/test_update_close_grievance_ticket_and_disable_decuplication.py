from datetime import date
from unittest import mock

from django_countries.fields import Country

from hct_mis_api.apps.account.fixtures import UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import (
    AdminAreaFactory,
    AdminAreaLevelFactory,
    create_afghanistan,
)
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
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
from hct_mis_api.apps.program.fixtures import ProgramFactory

# from hct_mis_api.apps.registration_datahub.tasks.deduplicate import DeduplicateTask


class TestUpdateCloseGrievanceTicketAndDisableDeduplication(APITestCase):
    UPDATE_GRIEVANCE_TICKET_STATUS_CHANGE_MUTATION = """
    mutation GrievanceTicketStatusChange($grievanceTicketId: ID, $status: Int) {
        grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
            grievanceTicket {
                id
                status
                createdAt
                updatedAt
                createdBy {
                    id
                    firstName
                    lastName
                    username
                    email
                }
            }
        }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory(id="a5c44eeb-482e-49c2-b5ab-d769f83db116")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="123333")
        cls.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="2343123")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1_new = AreaFactory(name="City Test", area_type=area_type, p_code="123333")
        cls.admin_area_2_new = AreaFactory(name="City Example", area_type=area_type, p_code="2343123")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07", size=2, village="Example")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        cls.individual = IndividualFactory(household=household_one)
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        cls.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=cls.individual
        )
        cls.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=cls.individual
        )
        household_one.head_of_household = cls.individual
        household_one.save()
        cls.household_one = household_one
        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=cls.user,
        )
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
                "documents": [{"type": IDENTIFICATION_TYPE_NATIONAL_ID, "country": "POL", "number": "123-123-UX-321"}],
            },
            approve_status=True,
        )

        cls.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=cls.user,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.individual_data_change_grievance_ticket,
            individual=cls.individual,
            individual_data={
                "given_name": {"value": "Test", "approve_status": True},
                "full_name": {"value": "Test Example", "approve_status": True},
                "family_name": {"value": "Example", "approve_status": True},
                "relationship": RELATIONSHIP_UNKNOWN,
                "estimated_birth_date": False,
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": True},
                "role": {"value": ROLE_PRIMARY, "approve_status": True},
                "documents": [
                    {
                        "value": {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "999-888-777"},
                        "approve_status": True,
                    },
                ],
                "documents_to_remove": [
                    {"value": cls.id_to_base64(cls.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": cls.id_to_base64(cls.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
            },
        )

    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_add_individual_close_ticket_for_postponed_deduplication(self):
        permissions = [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK_AS_CREATOR]
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.individual_data_change_grievance_ticket.postpone_deduplication = True
        self.individual_data_change_grievance_ticket.save()

        input_data = {
            "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
            "status": GrievanceTicket.STATUS_CLOSED,
        }

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )

        self.assertFalse("errors" in response)

        # DeduplicateTask
        self.individual.refresh_from_db()
        self.individual_data_change_grievance_ticket.refresh_from_db()

        self.assertEqual(self.individual_data_change_grievance_ticket.status, GrievanceTicket.STATUS_CLOSED)
        self.assertEqual(self.individual.deduplication_batch_status, UNIQUE_IN_BATCH)
        self.assertEqual(self.individual.deduplication_golden_record_results, dict())
