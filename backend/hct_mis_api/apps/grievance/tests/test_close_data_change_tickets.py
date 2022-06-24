from datetime import date

from django.core.management import call_command

from django_countries.fields import Country
from parameterized import parameterized

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
    TicketDeleteHouseholdDetailsFactory,
    TicketDeleteIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    ROLE_PRIMARY,
    SINGLE,
    BankAccountInfo,
    Document,
    DocumentType,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


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

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory.create()
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        area_type = AdminAreaLevelFactory(
            name="Admin type one",
            admin_level=2,
            business_area=cls.business_area,
        )
        cls.admin_area_1 = AdminAreaFactory(title="City Test", admin_area_level=area_type, p_code="sfds323")
        cls.admin_area_2 = AdminAreaFactory(title="City Example", admin_area_level=area_type, p_code="sfds3dgg23")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1_new = AreaFactory(name="City Test", area_type=area_type, p_code="sfds323")
        cls.admin_area_2_new = AreaFactory(name="City Example", area_type=area_type, p_code="sfds3dgg23")

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(id="07a901ed-d2a5-422a-b962-3570da1d5d07")
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.save()
        household_one.programs.add(program_one)

        household_two = HouseholdFactory.build(id="603dfd3f-baca-42d1-aac6-3e1c537ddbef")
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.save()
        household_two.programs.add(program_one)

        cls.individuals_to_create = [
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

        cls.individuals_to_create_for_second_household = [
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

        cls.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in cls.individuals_to_create
        ]
        cls.individuals_household_two = [
            IndividualFactory(household=household_two, **individual)
            for individual in cls.individuals_to_create_for_second_household
        ]

        first_individual = cls.individuals[0]
        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=Country("POL"), type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
        )
        cls.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=first_individual
        )
        cls.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=first_individual
        )
        household_one.head_of_household = cls.individuals[0]
        household_one.save()
        cls.household_one = household_one

        household_two.head_of_household = cls.individuals_household_two[0]
        household_two.save()
        cls.household_two = household_two
        cls.role_primary = IndividualRoleInHousehold.objects.create(
            role=ROLE_PRIMARY,
            individual=cls.individuals_household_two[0],
            household=household_two,
        )

        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketAddIndividualDetailsFactory(
            ticket=cls.add_individual_grievance_ticket,
            household=cls.household_one,
            individual_data={
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": date(year=1980, month=2, day=1).isoformat(),
                "marital_status": SINGLE,
                "role": ROLE_PRIMARY,
                "documents": [
                    {
                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                        "country": "POL",
                        "number": "123-123-UX-321",
                        "photo": "test_file_name.jpg",
                        "photoraw": "test_file_name.jpg",
                    }
                ],
                "payment_channels": [
                    {
                        "type": "BANK_TRANSFER",
                        "bank_name": "privatbank",
                        "bank_account_number": 2356789789789789,
                    },
                ],
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
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.individual_data_change_grievance_ticket,
            individual=cls.individuals[0],
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
                        "value": {
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                            "number": "999-888-777",
                            "photo": "test_file_name.jpg",
                            "photoraw": "test_file_name.jpg",
                        },
                        "approve_status": True,
                    },
                ],
                "documents_to_remove": [
                    {"value": cls.id_to_base64(cls.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": cls.id_to_base64(cls.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
            },
        )

        cls.household_data_change_grievance_ticket = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5410",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=cls.household_data_change_grievance_ticket,
            household=cls.household_one,
            household_data={
                "village": {"value": "Test Village", "approve_status": True},
            },
        )

        cls.individual_delete_grievance_ticket = GrievanceTicketFactory(
            id="a2a15944-f836-4764-8163-30e0c47ce3bb",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteIndividualDetailsFactory(
            ticket=cls.individual_delete_grievance_ticket,
            individual=cls.individuals_household_two[0],
            role_reassign_data={
                str(cls.role_primary.id): {
                    "role": ROLE_PRIMARY,
                    "household": cls.id_to_base64(cls.household_two.id, "HouseholdNode"),
                    "individual": cls.id_to_base64(cls.individuals_household_two[1].id, "IndividualNode"),
                },
                "HEAD": {
                    "role": HEAD,
                    "household": cls.id_to_base64(cls.household_two.id, "HouseholdNode"),
                    "individual": cls.id_to_base64(cls.individuals_household_two[1].id, "IndividualNode"),
                },
            },
            approve_status=True,
        )

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_add_individual(cls, _, permissions, should_close):
        cls.create_user_role_with_permissions(cls.user, permissions, cls.business_area)

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(cls.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        created_individual = Individual.objects.exclude(id="257f6f84-313c-43bd-8f0e-89b96c41a7d5").filter(
            given_name="Test",
            full_name="Test Example",
            family_name="Example",
            sex="MALE",
        )
        if should_close:
            cls.assertTrue(created_individual.exists())
            created_individual = created_individual.first()

            document = Document.objects.get(document_number="123-123-UX-321")
            cls.assertEqual(document.type.country, Country("POL"))
            cls.assertEqual(document.photo, "test_file_name.jpg")

            role = created_individual.households_and_roles.get(
                role=ROLE_PRIMARY, household=cls.household_one, individual=created_individual
            )
            cls.assertEqual(str(role.household.id), str(cls.household_one.id))

            bank_account_info = BankAccountInfo.objects.get(individual=created_individual)
            cls.assertEqual(bank_account_info.bank_name, "privatbank")
            cls.assertEqual(bank_account_info.bank_account_number, "2356789789789789")
        else:
            cls.assertFalse(created_individual.exists())

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_update_individual(cls, _, permissions, should_close):
        cls.create_user_role_with_permissions(cls.user, permissions, cls.business_area)

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(
                    cls.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = cls.individuals[0]
        individual.refresh_from_db()

        if should_close:
            cls.assertEqual(individual.given_name, "Test")
            cls.assertEqual(individual.full_name, "Test Example")
            cls.assertEqual(individual.family_name, "Example")
            cls.assertEqual(individual.marital_status, SINGLE)
            cls.assertNotEqual(individual.birth_date, date(year=1980, month=2, day=1))

            role = individual.households_and_roles.get(role=ROLE_PRIMARY, individual=individual)
            cls.assertEqual(str(role.household.id), str(cls.household_one.id))

            document = Document.objects.get(document_number="999-888-777")
            cls.assertEqual(document.type.country, Country("POL"))
            cls.assertEqual(document.type.type, IDENTIFICATION_TYPE_NATIONAL_ID)
            cls.assertEqual(document.photo, "test_file_name.jpg")

            cls.assertFalse(Document.objects.filter(id=cls.national_id.id).exists())
            cls.assertTrue(Document.objects.filter(id=cls.birth_certificate.id).exists())
        else:
            cls.assertEqual(individual.given_name, "Benjamin")
            cls.assertEqual(individual.full_name, "Benjamin Butler")
            cls.assertEqual(individual.family_name, "Butler")

    def test_close_update_individual_document_photo(cls):
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], cls.business_area
        )

        national_id_type = DocumentType.objects.get(country=Country("POL"), type=IDENTIFICATION_TYPE_NATIONAL_ID)
        national_id = DocumentFactory(
            type=national_id_type,
            document_number="999-888-777",
            individual=cls.individuals[0],
            photo="test_file_name.jpg",
        )

        grievance_ticket = GrievanceTicketFactory(
            id="32c3ae7d-fb39-4d69-8559-9d0fa4284790",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            individual=cls.individuals[0],
            individual_data={
                "documents_to_edit": [
                    {
                        "value": {
                            "id": cls.id_to_base64(national_id.id, "DocumentNode"),
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                            "number": "999-888-777",
                            "photo": "new_test_file_name.jpg",
                            "photoraw": "new_test_file_name.jpg",
                        },
                        "previous_value": {
                            "id": cls.id_to_base64(national_id.id, "DocumentNode"),
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                            "number": "999-888-777",
                            "photo": "test_file_name.jpg",
                            "photoraw": "test_file_name.jpg",
                        },
                        "approve_status": True,
                    },
                ],
            },
        )

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = cls.individuals[0]
        individual.refresh_from_db()

        document = Document.objects.get(document_number="999-888-777")
        cls.assertEqual(document.type.country, Country("POL"))
        cls.assertEqual(document.type.type, IDENTIFICATION_TYPE_NATIONAL_ID)
        cls.assertEqual(document.photo.name, "new_test_file_name.jpg")

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_update_household(cls, _, permissions, should_close):
        cls.create_user_role_with_permissions(cls.user, permissions, cls.business_area)
        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(
                    cls.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        cls.household_one.refresh_from_db()
        if should_close:
            cls.assertEqual(cls.household_one.village, "Test Village")

    def test_close_individual_delete_with_correct_permissions(cls):
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], cls.business_area
        )

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(cls.individual_delete_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        ind = Individual.objects.filter(id=cls.individuals_household_two[0].id).first()
        ind.refresh_from_db()
        cls.assertTrue(ind.withdrawn)
        changed_role_exists = IndividualRoleInHousehold.objects.filter(
            role=ROLE_PRIMARY, household=cls.household_two, individual=cls.individuals_household_two[1]
        ).exists()
        cls.assertTrue(changed_role_exists)

    def test_close_individual_delete_without_permissions(cls):
        cls.create_user_role_with_permissions(cls.user, [], cls.business_area)

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(cls.individual_delete_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        cls.assertTrue(Individual.objects.filter(id=cls.individuals_household_two[0].id).exists())

    def test_close_household_delete(cls):
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], cls.business_area
        )

        grievance_ticket = GrievanceTicketFactory(
            id="32c3ae7d-fb39-4d69-8559-9d0fa4284790",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
            admin2=cls.admin_area_1,
            admin2_new=cls.admin_area_1_new,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketDeleteHouseholdDetailsFactory(
            ticket=grievance_ticket,
            household=cls.household_one,
            approve_status=True,
        )

        cls.graphql_request(
            request_string=cls.STATUS_CHANGE_MUTATION,
            context={"user": cls.user},
            variables={
                "grievanceTicketId": cls.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )

        cls.household_one.refresh_from_db()
        cls.individuals[0].refresh_from_db()
        cls.individuals[1].refresh_from_db()

        cls.assertTrue(cls.household_one.withdrawn)
        cls.assertTrue(cls.individuals[0].withdrawn)
        cls.assertTrue(cls.individuals[1].withdrawn)

    def test_close_add_individual_create_bank_account(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        created_individual = (
            Individual.objects.exclude(id="257f6f84-313c-43bd-8f0e-89b96c41a7d5")
            .filter(
                given_name="Test",
                full_name="Test Example",
                family_name="Example",
                sex="MALE",
            )
            .first()
        )

        bank_account_info = BankAccountInfo.objects.get(individual=created_individual)
        self.assertEqual(bank_account_info.bank_name, "privatbank")
        self.assertEqual(bank_account_info.bank_account_number, "2356789789789789")

    def test_close_update_individual_create_bank_account(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )

        ticket = GrievanceTicketFactory(
            id="9dc794ba-b59a-4acf-a7cb-6590d879e86e",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=self.admin_area_1,
            admin2_new=self.admin_area_1_new,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=ticket,
            individual=self.individuals[0],
            individual_data={
                "payment_channels": [
                    {
                        "value": {
                            "type": "BANK_TRANSFER",
                            "bank_name": "privatbank",
                            "bank_account_number": 2356789789789789,
                        },
                        "approve_status": True,
                    },
                ],
            },
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        bank_account_info = BankAccountInfo.objects.get(individual=individual)
        self.assertEqual(bank_account_info.bank_name, "privatbank")
        self.assertEqual(bank_account_info.bank_account_number, "2356789789789789")

    def test_close_update_individual_update_bank_account(self):
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )

        ticket = GrievanceTicketFactory(
            id="9dc794ba-b59a-4acf-a7cb-6590d879e86e",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=self.admin_area_1,
            admin2_new=self.admin_area_1_new,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        BankAccountInfoFactory(
            id="413b2a07-4bc1-43a7-80e6-91abb486aa9d",
            individual=self.individuals[0],
            bank_name="privatbank",
            bank_account_number=2356789789789789,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=ticket,
            individual=self.individuals[0],
            individual_data={
                "payment_channels_to_edit": [
                    {
                        "approve_status": True,
                        "previous_value": {
                            "bank_account_number": "2356789789789789",
                            "bank_name": "privatbank",
                            "id": "QmFua0FjY291bnRJbmZvTm9kZTo0MTNiMmEwNy00YmMxLTQzYTctODBlNi05MWFiYjQ4NmFhOWQ=",
                            "individual": "SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh",
                            "type": "BANK_TRANSFER",
                        },
                        "value": {
                            "bank_account_number": "1111222233334444",
                            "bank_name": "privatbank",
                            "id": "QmFua0FjY291bnRJbmZvTm9kZTo0MTNiMmEwNy00YmMxLTQzYTctODBlNi05MWFiYjQ4NmFhOWQ=",
                            "individual": "SW5kaXZpZHVhbE5vZGU6YjZmZmIyMjctYTJkZC00MTAzLWJlNDYtMGM5ZWJlOWYwMDFh",
                            "type": "BANK_TRANSFER",
                        },
                    }
                ],
            },
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user},
            variables={
                "grievanceTicketId": self.id_to_base64(ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        bank_account_info = BankAccountInfo.objects.get(individual=individual)
        self.assertEqual(bank_account_info.bank_name, "privatbank")
        self.assertEqual(bank_account_info.bank_account_number, "1111222233334444")
