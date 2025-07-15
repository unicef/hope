import uuid
from datetime import date
from typing import Any, List

from django.core.management import call_command

import pytest
from flaky import flaky
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
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
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    HEAD,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    NOT_ANSWERED,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SINGLE,
    Document,
    DocumentType,
    Individual,
    IndividualRoleInHousehold,
)
from hct_mis_api.apps.payment.fixtures import (
    AccountFactory,
    FinancialInstitutionFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import AccountType
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.usefixtures("django_elasticsearch_setup")


@pytest.mark.elasticsearch
@flaky
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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()

        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory.create(partner=partner)
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type1 = AreaTypeFactory(
            name="Admin type level one",
            country=country,
            area_level=1,
        )
        area_type2 = AreaTypeFactory(
            parent=area_type1,
            name="Admin type level two",
            country=country,
            area_level=2,
        )
        admin_area = AreaFactory(name="City Test 1", area_type=area_type1, p_code="sfds")
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type2, p_code="sfds323", parent=admin_area)
        cls.admin_area_2 = AreaFactory(
            name="City Example", area_type=area_type2, p_code="sfds3dgg23", parent=admin_area
        )

        program_one = ProgramFactory(
            name="Test program ONE",
            business_area=BusinessArea.objects.first(),
        )

        cls.program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )
        cls.update_partner_access_to_program(partner, cls.program)
        cls.update_partner_access_to_program(partner, program_one)

        household_one = HouseholdFactory.build(admin_area=cls.admin_area_1, program=cls.program)
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = program_one
        household_one.registration_data_import.save()
        household_one.program = program_one

        household_two = HouseholdFactory.build(admin_area=cls.admin_area_1, program=cls.program)
        household_two.household_collection.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.program = program_one
        household_two.registration_data_import.save()
        household_two.program = program_one

        cls.individuals_to_create = [
            {
                "pk": "df1ce6e8-2864-4c3f-803d-19ec6f4c4111",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
            },
            {
                "pk": "df1ce6e8-2864-4c3f-803d-19ec6f4c4222",
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
                "unicef_id": "IND-1111",
            },
            {
                "id": "cd5ced0f-3777-47d8-92ca-5b3aa22f186d",
                "full_name": "John Doe",
                "given_name": "John",
                "family_name": "Doe",
                "phone_no": "+12315124125",
                "birth_date": "1975-07-25",
                "unicef_id": "IND-2222",
            },
        ]

        cls.individuals = [
            IndividualFactory(
                household=household_one, program=program_one, **individual | {"unicef_id": str(uuid.uuid4())}
            )
            for individual in cls.individuals_to_create
        ]
        cls.individuals_household_two = [
            IndividualFactory(
                household=household_two, program=program_one, **individual | {"unicef_id": str(uuid.uuid4())}
            )
            for individual in cls.individuals_to_create_for_second_household
        ]

        first_individual = cls.individuals[0]

        cls.fi1 = FinancialInstitutionFactory(id="6")
        cls.fi2 = FinancialInstitutionFactory(id="7")
        cls.account = AccountFactory(
            id=uuid.UUID("e0a7605f-62f4-4280-99f6-b7a2c4001680"),
            individual=first_individual,
            number="123",
            data={"field": "value"},
            financial_institution=cls.fi1,
            account_type=AccountType.objects.get(key="mobile"),
        )

        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        birth_certificate_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )
        cls.national_id = DocumentFactory(
            type=national_id_type, document_number="789-789-645", individual=first_individual, country=country_pl
        )
        cls.birth_certificate = DocumentFactory(
            type=birth_certificate_type, document_number="ITY8456", individual=first_individual, country=country_pl
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
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=cls.admin_area_1,
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
                        "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                        "country": "POL",
                        "number": "123-123-UX-321",
                        "photo": "test_file_name.jpg",
                        "photoraw": "test_file_name.jpg",
                    }
                ],
            },
            approve_status=True,
        )

        cls.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
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
                "phone_no_alternative": {"value": "+48602203689", "approve_status": True},
                "sex": {"value": "NOT_ANSWERED", "approve_status": True},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": True},
                "role": {"value": ROLE_PRIMARY, "approve_status": True},
                "documents": [
                    {
                        "value": {
                            "country": "POL",
                            "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
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
                "accounts": [
                    {
                        "approve_status": True,
                        "value": {
                            "data_fields": {
                                "financial_institution": str(cls.fi1.id),
                                "new_field": "new_value",
                                "number": "2222",
                            },
                            "name": "mobile",
                        },
                    }
                ],
                "accounts_to_edit": [
                    {
                        "approve_status": True,
                        "data_fields": [
                            {"name": "field", "previous_value": "value", "value": "updated_value"},
                            {"name": "new_field", "previous_value": None, "value": "new_value"},
                            {"name": "number", "previous_value": "123", "value": "123123"},
                            {
                                "name": "financial_institution",
                                "previous_value": str(cls.fi1.id),
                                "value": str(cls.fi2.id),
                            },
                        ],
                        "id": "QWNjb3VudE5vZGU6ZTBhNzYwNWYtNjJmNC00MjgwLTk5ZjYtYjdhMmM0MDAxNjgw",
                        "name": "mobile",
                    }
                ],
            },
        )

        cls.household_data_change_grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=cls.admin_area_1,
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
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_INDIVIDUAL,
            admin2=cls.admin_area_1,
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

        rebuild_search_index()

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_add_individual(self, _: Any, permissions: List[Permissions], should_close: bool) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
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
            self.assertTrue(created_individual.exists())
            created_individual = created_individual.first()

            document = Document.objects.get(document_number="123-123-UX-321")
            country_pl = geo_models.Country.objects.get(iso_code2="PL")
            self.assertEqual(document.country, country_pl)
            self.assertEqual(document.photo, "test_file_name.jpg")

            role = created_individual.households_and_roles.get(
                role=ROLE_PRIMARY, household=self.household_one, individual=created_individual
            )
            self.assertEqual(str(role.household.id), str(self.household_one.id))

        else:
            self.assertFalse(created_individual.exists())

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_update_individual(self, _: Any, permissions: List[Permissions], should_close: bool) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        if should_close:
            self.assertEqual(individual.given_name, "Test")
            self.assertEqual(individual.full_name, "Test Example")
            self.assertEqual(individual.family_name, "Example")
            self.assertEqual(individual.phone_no_alternative, "+48602203689")
            self.assertEqual(individual.phone_no_alternative_valid, True)
            self.assertEqual(individual.marital_status, SINGLE)
            self.assertEqual(individual.sex, NOT_ANSWERED)
            self.assertNotEqual(individual.birth_date, date(year=1980, month=2, day=1))

            role = individual.households_and_roles.get(role=ROLE_PRIMARY, individual=individual)
            self.assertEqual(str(role.household.id), str(self.household_one.id))

            document = Document.objects.get(document_number="999-888-777")
            country_pl = geo_models.Country.objects.get(iso_code2="PL")

            self.assertEqual(document.country, country_pl)
            self.assertEqual(document.type.key, IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID])
            self.assertEqual(document.photo, "test_file_name.jpg")

            self.assertFalse(Document.objects.filter(id=self.national_id.id).exists())
            self.assertTrue(Document.objects.filter(id=self.birth_certificate.id).exists())

            self.account.refresh_from_db()
            self.assertEqual(self.account.number, "123123")
            self.assertEqual(self.account.financial_institution, self.fi2)
            self.assertEqual(
                self.account.data,
                {
                    "field": "updated_value",
                    "new_field": "new_value",
                },
            )

            new_account = individual.accounts.exclude(id=self.account.id).first()
            self.assertEqual(new_account.number, "2222")
            self.assertEqual(new_account.financial_institution, self.fi1)
            self.assertEqual(
                new_account.data,
                {
                    "new_field": "new_value",
                },
            )

        else:
            self.assertEqual(individual.given_name, "Benjamin")
            self.assertEqual(individual.full_name, "Benjamin Butler")
            self.assertEqual(individual.family_name, "Butler")

    def test_close_update_individual_document_photo(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )
        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        national_id = DocumentFactory(
            type=national_id_type,
            document_number="999-888-777",
            individual=self.individuals[0],
            photo="test_file_name.jpg",
            country=country_pl,
        )

        grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=self.admin_area_1,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=grievance_ticket,
            individual=self.individuals[0],
            individual_data={
                "documents_to_edit": [
                    {
                        "value": {
                            "id": self.id_to_base64(national_id.id, "DocumentNode"),
                            "country": "POL",
                            "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                            "number": "999-888-777",
                            "photo": "new_test_file_name.jpg",
                            "photoraw": "new_test_file_name.jpg",
                        },
                        "previous_value": {
                            "id": self.id_to_base64(national_id.id, "DocumentNode"),
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                            "number": "999-888-777",
                            "photo": "test_file_name.jpg",
                            "photoraw": "test_file_name.jpg",
                        },
                        "approve_status": True,
                    },
                ],
            },
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(grievance_ticket.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        individual = self.individuals[0]
        individual.refresh_from_db()

        document = Document.objects.get(document_number="999-888-777")
        self.assertEqual(document.country, country_pl)
        self.assertEqual(document.type.key, IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID])
        self.assertEqual(document.photo.name, "new_test_file_name.jpg")

    @parameterized.expand(
        [
            ("with_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], True),
            ("without_permission", [Permissions.GRIEVANCES_CLOSE_TICKET_FEEDBACK], False),
        ]
    )
    def test_close_update_household(self, _: Any, permissions: List[Permissions], should_close: bool) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.household_one.refresh_from_db()
        if should_close:
            self.assertEqual(self.household_one.village, "Test Village")

    def test_close_individual_delete_with_correct_permissions(self) -> None:
        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_delete_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        ind = Individual.objects.filter(id=self.individuals_household_two[0].id).first()
        ind.refresh_from_db()
        self.assertTrue(ind.withdrawn)
        changed_role_exists = IndividualRoleInHousehold.objects.filter(
            role=ROLE_PRIMARY, household=self.household_two, individual=self.individuals_household_two[1]
        ).exists()
        self.assertTrue(changed_role_exists)

    def test_close_individual_delete_without_permissions(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(
                    self.individual_delete_grievance_ticket.id, "GrievanceTicketNode"
                ),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )
        self.assertTrue(Individual.objects.filter(id=self.individuals_household_two[0].id).exists())

    def test_close_household_delete(cls) -> None:
        cls.create_user_role_with_permissions(
            cls.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], cls.business_area
        )

        grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_DELETE_HOUSEHOLD,
            admin2=cls.admin_area_1,
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

    def test_close_household_update_new_roles(self) -> None:
        first_individual = self.individuals[0]
        second_individual = self.individuals[1]
        # add ALTERNATE role for first_individual
        IndividualRoleInHousehold.objects.create(
            household=self.household_one,
            individual=first_individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        household_data_change_grv_new = GrievanceTicketFactory(
            id="72ee7d98-6108-4ef0-85bd-2ef20e1d5444",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=self.admin_area_1,
            business_area=self.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
        )
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=household_data_change_grv_new,
            household=self.household_one,
            household_data={
                "village": {
                    "value": "Test new",
                    "approve_status": True,
                },
                "flex_fields": {},
                "roles": [
                    {
                        "value": "PRIMARY",
                        "individual_id": self.id_to_base64(str(first_individual.id), "IndividualNode"),
                        "approve_status": True,
                        "previous_value": "ALTERNATE",
                    },
                    {
                        "value": "ALTERNATE",
                        "individual_id": self.id_to_base64(str(second_individual.id), "IndividualNode"),
                        "approve_status": True,
                        "previous_value": "-",
                    },
                ],
            },
        )
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=self.household_one).count(), 1)
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=first_individual).role, "ALTERNATE")

        self.create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_CLOSE_TICKET_EXCLUDING_FEEDBACK], self.business_area
        )
        self.graphql_request(
            request_string=self.STATUS_CHANGE_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables={
                "grievanceTicketId": self.id_to_base64(household_data_change_grv_new.id, "GrievanceTicketNode"),
                "status": GrievanceTicket.STATUS_CLOSED,
            },
        )

        # check if role updated and new one created for second_individual
        self.assertEqual(IndividualRoleInHousehold.objects.filter(household=self.household_one).count(), 2)
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=first_individual).role, "PRIMARY")
        self.assertEqual(IndividualRoleInHousehold.objects.get(individual=second_individual).role, "ALTERNATE")
