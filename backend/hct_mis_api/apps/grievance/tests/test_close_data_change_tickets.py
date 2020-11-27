from datetime import date

from django.core.management import call_command
from django_countries.fields import Country

from account.fixtures import UserFactory
from core.base_test_case import APITestCase
from core.fixtures import AdminAreaTypeFactory, AdminAreaFactory
from core.models import BusinessArea
from grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
)
from grievance.models import GrievanceTicket
from household.fixtures import HouseholdFactory, IndividualFactory, DocumentFactory
from household.models import (
    SINGLE,
    Individual,
    ROLE_PRIMARY,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    Document,
    DocumentType,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IndividualRoleInHousehold,
    ROLE_ALTERNATE,
    HEAD,
)
from program.fixtures import ProgramFactory


class TestCloseDataChangeTickets(APITestCase):
    STATUS_CHANGE_MUTATION = """
    mutation GrievanceStatusChange($grievanceTicketId: ID!, $status: Int) {
      grievanceStatusChange(grievanceTicketId: $grievanceTicketId, status: $status) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            individualData
          }
        }
      }
    }
    """

    def setUp(self):
        super().setUp()
        call_command("loadbusinessareas")
        self.generate_document_types_for_all_countries()
        self.user = UserFactory.create()
        self.business_area = BusinessArea.objects.get(slug="afghanistan")
        area_type = AdminAreaTypeFactory(name="Admin type one", admin_level=2, business_area=self.business_area,)
        self.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_type=area_type)
        self.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_type=area_type)
        program_one = ProgramFactory(name="Test program ONE", business_area=BusinessArea.objects.first(),)

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        household_two = HouseholdFactory.build(id="603dfd3f-baca-42d1-aac6-3e1c537ddbef")
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.save()
        household_two.programs.add(program_one)

        self.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
            },
        ]

        self.individuals_to_create_for_second_household = [
            {
                "id": "257f6f84-313c-43bd-8f0e-89b96c41a7d5",
                "full_name": "Test Example",
                "given_name": "Test",
                "family_name": "Example",
                "phone_no": "+18773523904",
                "birth_date": "1965-03-15",
            },
            {
                "id": "cd5ced0f-3777-47d8-92ca-5b3aa22f186d",
                "full_name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "phone_no": "+12315124125",
                "birth_date": "1975-07-25",
            },
        ]

        self.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in self.individuals_to_create
        ]
        self.individuals_household_two = [
            IndividualFactory(household=household_two, **individual)
            for individual in self.individuals_to_create_for_second_household
        ]

        first_individual = self.individuals[0]
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        self.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=first_individual
        )
        self.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=first_individual
        )
        household_one.head_of_household = self.individuals[0]
        household_one.save()
        self.household_one = household_one

        household_two.head_of_household = self.individuals_household_two[0]
        household_two.save()
        self.household_two = household_two
        self.role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY, individual=self.individuals_household_two[0], household=household_two,
        )

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketAddIndividualDetailsFactory(
            ticket=self.add_individual_grievance_ticket,
            household=self.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "role": ROLE_PRIMARY,
                "documents": [{"type": IDENTIFICATION_TYPE_NATIONAL_ID, "country": "POL", "number": "123-123-UX-321"}],
            },
            approve_status=True,
        )

        self.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test", "approve_status": True},
                "full_name": {"value": "Test Example", "approve_status": True},
                "family_name": {"value": "Example", "approve_status": True},
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
                    {"value": self.id_to_base64(self.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": self.id_to_base64(self.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
            },
        )

        self.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={
                "village": {"value": "Test Village", "approve_status": True},
                "size": {"value": 19, "approve_status": True},
            },
        )

        self.individual_delete_grievance_ticket = GrievanceTicketFactory(
            id="a2a15944-f836-4764-8163-30e0c47ce3bb",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin=self.admin_area_1.title,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=self.individual_delete_grievance_ticket,
            individual=self.individuals_household_two[0],
            role_reassign_data={
                str(self.role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": str(self.household_two.id),
                    "individual": str(self.individuals_household_two[1].id),
                },
                f"HEAD": {
                    "role": HEAD,
                    "household": str(self.household_two.id),
                    "individual": str(self.individuals_household_two[1].id),
                },
            },
            approve_status=True,
        )

    def test_close_add_individual(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        created_individual = Individual.objects.filter(
            given_name="Test", full_name="Test Example", family_name="Example", sex="MALE",
        )
        self.assertTrue(created_individual.exists())

        created_individual = created_individual.first()

        document = Document.objects.get(document_number="123-123-UX-321")
        self.assertEqual(document.type.country, Country("POL"))

        role = created_individual.households_and_roles.get(
            role=ROLE_PRIMARY, household=self.household_one, individual=created_individual
        )
        self.assertEqual(str(role.household.id), str(self.household_one.id))

    def test_close_update_individual(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        self.assertEqual(individual.given_name, "Test")
        self.assertEqual(individual.full_name, "Test Example")
        self.assertEqual(individual.family_name, "Example")
        self.assertEqual(individual.marital_status, SINGLE)
        self.assertNotEqual(individual.birth_date, date(year=1980, month=2, day=1))

        role = individual.households_and_roles.get(role=ROLE_PRIMARY, individual=individual)
        self.assertEqual(str(role.household.id), str(self.household_one.id))

        document = Document.objects.get(document_number="999-888-777")
        self.assertEqual(document.type.country, Country("POL"))
        self.assertEqual(document.type.type, IDENTIFICATION_TYPE_NATIONAL_ID)

        self.assertFalse(Document.objects.filter(id=self.national_id.id).exists())
        self.assertTrue(Document.objects.filter(id=self.birth_certificate.id).exists())

    def test_close_update_household(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.household_one.refresh_from_db()
        self.assertEqual(self.household_one.size, 19)
        self.assertEqual(self.household_one.village, "Test Village")

    def test_close_individual_delete(self):
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_delete_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.assertFalse(Individual.objects.filter(id=self.individuals_household_two[0].id).exists())
        changed_role_exists = IndividualRoleInHousehold.objects.filter(
            role=ROLE_PRIMARY, household=self.household_two, individual=self.individuals_household_two[1]
        ).exists()
        self.assertTrue(changed_role_exists)
