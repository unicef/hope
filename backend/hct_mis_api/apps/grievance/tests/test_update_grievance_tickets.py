from datetime import date
from unittest import mock

from django.core.files.uploadedfile import SimpleUploadedFile
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
    GrievanceComplaintTicketWithoutExtrasFactory,
    GrievanceTicketFactory,
    PositiveFeedbackTicketWithoutExtrasFactory,
    SensitiveGrievanceTicketWithoutExtrasFactory,
    TicketAddIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import GrievanceTicket
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    create_household,
)
from hct_mis_api.apps.household.models import (
    DIVORCED,
    FEMALE,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    MALE,
    RELATIONSHIP_UNKNOWN,
    ROLE_PRIMARY,
    SINGLE,
    UNHCR,
    Agency,
    DocumentType,
    IndividualIdentity,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory


class TestUpdateGrievanceTickets(APITestCase):
    UPDATE_GRIEVANCE_TICKET_MUTATION = """
    mutation UpdateGrievanceTicket(
      $input: UpdateGrievanceTicketInput!
    ) {
      updateGrievanceTicket(input: $input) {
        grievanceTicket {
          id
          addIndividualTicketDetails {
            individualData
          }
          householdDataUpdateTicketDetails {
            householdData
          }
          individualDataUpdateTicketDetails {
            individualData
          }
          description
          assignedTo {
            id
          }
          status
          area
          admin
          description
          language
        }
      }
    }
    """

    @classmethod
    def setUpTestData(cls):
        create_afghanistan()
        call_command("loadcountries")
        cls.generate_document_types_for_all_countries()
        cls.user = UserFactory(id="a5c44eeb-482e-49c2-b5ab-d769f83db116")
        cls.user_two = UserFactory(id="a34716d8-aaf1-4c70-bdd8-0d58be94981a")
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

        cls.individuals_to_create = [
            {
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "sex": FEMALE,
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "marital_status": DIVORCED,
            },
            {
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "sex": FEMALE,
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "marital_status": DIVORCED,
            },
        ]

        cls.individuals = [
            IndividualFactory(household=household_one, **individual) for individual in cls.individuals_to_create
        ]

        first_individual = cls.individuals[0]
        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(country=country_pl, type=IDENTIFICATION_TYPE_NATIONAL_ID)
        birth_certificate_type = DocumentType.objects.get(
            country=country_pl, type=IDENTIFICATION_TYPE_BIRTH_CERTIFICATE
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
        )
        TicketIndividualDataUpdateDetailsFactory(
            ticket=cls.individual_data_change_grievance_ticket,
            individual=cls.individuals[0],
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
                "size": {"value": 19, "approve_status": True},
                "country": "AFG",
            },
        )

        cls.positive_feedback_grievance_ticket = GrievanceTicketFactory(
            id="a2a15944-f836-4764-8163-30e0c47ce3bb",
            category=GrievanceTicket.CATEGORY_POSITIVE_FEEDBACK,
            issue_type=None,
            business_area=cls.business_area,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            description="",
            language="Spanish",
            admin2=cls.admin_area_2,
            admin2_new=cls.admin_area_2_new,
        )
        PositiveFeedbackTicketWithoutExtrasFactory(ticket=cls.positive_feedback_grievance_ticket)

        unhcr_agency = Agency.objects.create(type="UNHCR", label="UNHCR", country="POL")
        cls.identity_to_update = IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individuals[0],
            number="1111",
        )

        cls.identity_to_remove = IndividualIdentity.objects.create(
            agency=unhcr_agency,
            individual=cls.individuals[0],
            number="3456",
        )

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
            ),
            (
                "with_partial_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_update_add_individual(self, name, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.add_individual_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.add_individual_grievance_ticket.save()
        input_data = {
            "input": {
                "description": self.add_individual_grievance_ticket.description,
                "assignedTo": self.id_to_base64(self.add_individual_grievance_ticket.assigned_to.id, "UserNode"),
                "admin": self.add_individual_grievance_ticket.admin2.p_code,
                "language": self.add_individual_grievance_ticket.language,
                "area": self.add_individual_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.add_individual_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "addIndividualIssueTypeExtras": {
                        "individualData": {
                            "givenName": "John",
                            "fullName": "John Example",
                            "familyName": "Example",
                            "relationship": RELATIONSHIP_UNKNOWN,
                            "estimatedBirthDate": False,
                            "sex": "MALE",
                            "birthDate": date(year=1981, month=2, day=2).isoformat(),
                            "maritalStatus": SINGLE,
                            "role": ROLE_PRIMARY,
                            "documents": [
                                {
                                    "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                                    "country": "USA",
                                    "number": "321-321-UX-321",
                                    "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                }
                            ],
                            "identities": [
                                {
                                    "agency": UNHCR,
                                    "country": "POL",
                                    "number": "2222",
                                }
                            ],
                            "paymentChannels": [
                                {
                                    "type": "BANK_TRANSFER",
                                    "bankName": "privatbank",
                                    "bankAccountNumber": 2356789789789789,
                                },
                            ],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
        self.add_individual_grievance_ticket.refresh_from_db()
        result = self.add_individual_grievance_ticket.add_individual_ticket_details.individual_data
        if name == "with_permission":
            expected_result = {
                "sex": "MALE",
                "role": "PRIMARY",
                "documents": [
                    {
                        "type": "NATIONAL_ID",
                        "number": "321-321-UX-321",
                        "country": "USA",
                        "photo": "test_file_name.jpg",
                        "photoraw": "test_file_name.jpg",
                    }
                ],
                "payment_channels": [
                    {
                        "type": "BANK_TRANSFER",
                        "bank_name": "privatbank",
                        "bank_account_number": "2356789789789789",
                    },
                ],
                "identities": [{"agency": "UNHCR", "country": "POL", "number": "2222"}],
                "full_name": "John Example",
                "birth_date": "1981-02-02",
                "given_name": "John",
                "family_name": "Example",
                "flex_fields": {},
                "relationship": "UNKNOWN",
                "marital_status": "SINGLE",
                "estimated_birth_date": False,
            }
            self.assertFalse(self.add_individual_grievance_ticket.add_individual_ticket_details.approve_status)

        else:
            expected_result = {
                "given_name": "Test",
                "full_name": "Test Example",
                "family_name": "Example",
                "sex": "MALE",
                "birth_date": "1980-02-01",
                "marital_status": "SINGLE",
                "role": "PRIMARY",
                "documents": [{"type": "NATIONAL_ID", "country": "POL", "number": "123-123-UX-321"}],
                "relationship": "UNKNOWN",
                "estimated_birth_date": False,
            }
            self.assertTrue(self.add_individual_grievance_ticket.add_individual_ticket_details.approve_status)

        self.assertEqual(result, expected_result)
        if name == "without_permission":
            self.assertEqual(self.add_individual_grievance_ticket.status, GrievanceTicket.STATUS_FOR_APPROVAL)
        else:
            self.assertEqual(self.add_individual_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
            ),
            (
                "with_partial_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    @mock.patch("django.core.files.storage.default_storage.save", lambda filename, file: "test_file_name.jpg")
    def test_update_change_individual(self, name, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.individual_data_change_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.individual_data_change_grievance_ticket.save()
        input_data = {
            "input": {
                "description": self.individual_data_change_grievance_ticket.description,
                "assignedTo": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.assigned_to.id, "UserNode"
                ),
                "admin": self.individual_data_change_grievance_ticket.admin2.p_code,
                "language": self.individual_data_change_grievance_ticket.language,
                "area": self.individual_data_change_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.individual_data_change_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "individualDataUpdateIssueTypeExtras": {
                        "individualData": {
                            "givenName": "John",
                            "fullName": "John Example",
                            "familyName": "Example",
                            "sex": MALE,
                            "birthDate": date(year=1962, month=12, day=21).isoformat(),
                            "maritalStatus": SINGLE,
                            "role": ROLE_PRIMARY,
                            "documents": [
                                {
                                    "country": "POL",
                                    "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                                    "number": "111-222-777",
                                    "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                },
                            ],
                            "documentsToRemove": [],
                            "identities": [
                                {
                                    "agency": UNHCR,
                                    "country": "POL",
                                    "number": "2222",
                                }
                            ],
                            "identitiesToEdit": [
                                {
                                    "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                                    "agency": UNHCR,
                                    "country": "POL",
                                    "number": "3333",
                                }
                            ],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
        self.individual_data_change_grievance_ticket.refresh_from_db()
        result = self.individual_data_change_grievance_ticket.individual_data_update_ticket_details.individual_data
        if name == "with_permission":
            expected_result = {
                "sex": {"value": "MALE", "approve_status": False, "previous_value": "FEMALE"},
                "role": {"value": "PRIMARY", "approve_status": False, "previous_value": "NO_ROLE"},
                "documents": [
                    {
                        "value": {
                            "type": "NATIONAL_ID",
                            "number": "111-222-777",
                            "country": "POL",
                            "photo": "test_file_name.jpg",
                            "photoraw": "test_file_name.jpg",
                        },
                        "approve_status": False,
                    },
                ],
                "identities": [
                    {
                        "value": {"agency": "UNHCR", "number": "2222", "country": "POL"},
                        "approve_status": False,
                    },
                ],
                "identities_to_edit": [
                    {
                        "value": {
                            "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                            "agency": "UNHCR",
                            "number": "3333",
                            "country": "POL",
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                        },
                        "previous_value": {
                            "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                            "agency": "UNHCR",
                            "number": "1111",
                            "country": "POL",
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                        },
                        "approve_status": False,
                    },
                ],
                "full_name": {"value": "John Example", "approve_status": False, "previous_value": "Benjamin Butler"},
                "birth_date": {"value": "1962-12-21", "approve_status": False, "previous_value": "1943-07-30"},
                "given_name": {"value": "John", "approve_status": False, "previous_value": "Benjamin"},
                "family_name": {"value": "Example", "approve_status": False, "previous_value": "Butler"},
                "flex_fields": {},
                "marital_status": {"value": "SINGLE", "approve_status": False, "previous_value": "DIVORCED"},
                "payment_channels": [],
                "payment_channels_to_edit": [],
                "payment_channels_to_remove": [],
                "previous_payment_channels": {},
                "documents_to_edit": [],
                "previous_documents": {},
                "documents_to_remove": [],
                "previous_identities": {},
                "identities_to_remove": [],
            }

        else:
            expected_result = {
                "sex": {"value": "MALE", "approve_status": False},
                "role": {"value": "PRIMARY", "approve_status": True},
                "documents": [
                    {
                        "value": {"type": "NATIONAL_ID", "number": "999-888-777", "country": "POL"},
                        "approve_status": True,
                    }
                ],
                "full_name": {"value": "Test Example", "approve_status": True},
                "birth_date": {"value": "1980-02-01", "approve_status": False},
                "given_name": {"value": "Test", "approve_status": True},
                "family_name": {"value": "Example", "approve_status": True},
                "relationship": "UNKNOWN",
                "marital_status": {"value": "SINGLE", "approve_status": True},
                "documents_to_remove": [
                    {"value": self.id_to_base64(self.national_id.id, "DocumentNode"), "approve_status": True},
                    {"value": self.id_to_base64(self.birth_certificate.id, "DocumentNode"), "approve_status": False},
                ],
                "estimated_birth_date": False,
            }
        self.assertEqual(result, expected_result)
        if name == "without_permission":
            self.assertEqual(self.individual_data_change_grievance_ticket.status, GrievanceTicket.STATUS_FOR_APPROVAL)
        else:
            self.assertEqual(self.individual_data_change_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
            ),
            (
                "with_partial_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_change_household(self, name, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "this is new description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": self.household_data_change_grievance_ticket.admin2.p_code,
                "language": self.household_data_change_grievance_ticket.language,
                "area": self.household_data_change_grievance_ticket.area,
                "ticketId": self.id_to_base64(self.household_data_change_grievance_ticket.id, "GrievanceTicketNode"),
                "extras": {
                    "householdDataUpdateIssueTypeExtras": {
                        "householdData": {
                            "village": "Test Town",
                            "size": 3,
                            "country": "AFG",
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
        self.household_data_change_grievance_ticket.refresh_from_db()
        result = self.household_data_change_grievance_ticket.household_data_update_ticket_details.household_data

        if name == "with_permission":
            expected_result = {
                "size": {"value": 3, "approve_status": False, "previous_value": 2},
                "country": {
                    "value": "AFG",
                    "approve_status": False,
                    "previous_value": self.household_one.country.iso_code3,
                },
                "village": {"value": "Test Town", "approve_status": False, "previous_value": "Example"},
                "flex_fields": {},
            }
        else:
            expected_result = {
                "village": {"value": "Test Village", "approve_status": True},
                "size": {"value": 19, "approve_status": True},
                "country": "AFG",
            }
        self.assertEqual(result, expected_result)
        if name in ["with_permission", "with_partial_permission"]:
            self.assertEqual(str(self.household_data_change_grievance_ticket.assigned_to.id), self.user_two.id)
            self.assertNotEqual(self.household_data_change_grievance_ticket.description, "this is new description")
            self.assertEqual(self.household_data_change_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)
        else:
            self.assertNotEqual(str(self.household_data_change_grievance_ticket.assigned_to.id), self.user_two.id)
            self.assertNotEqual(self.household_data_change_grievance_ticket.description, "this is new description")
            self.assertEqual(self.household_data_change_grievance_ticket.status, GrievanceTicket.STATUS_FOR_APPROVAL)

    @parameterized.expand(
        [
            (
                "with_permission",
                [Permissions.GRIEVANCES_UPDATE],
            ),
            ("without_permission", []),
        ]
    )
    def test_update_feedback_ticket(self, name, permissions):
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "New Description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": self.admin_area_1_new.p_code,
                "language": "Polish, English",
                "area": "Example Town",
                "ticketId": self.id_to_base64(self.positive_feedback_grievance_ticket.id, "GrievanceTicketNode"),
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=input_data,
        )
        self.positive_feedback_grievance_ticket.refresh_from_db()

        if name == "with_permission":
            self.assertEqual(self.positive_feedback_grievance_ticket.description, "New Description")
            self.assertEqual(str(self.positive_feedback_grievance_ticket.assigned_to.id), self.user_two.id)
            self.assertEqual(self.positive_feedback_grievance_ticket.admin2.title, self.admin_area_1.title)
            self.assertEqual(self.positive_feedback_grievance_ticket.admin2_new.name, self.admin_area_1_new.name)
            self.assertNotEqual(self.positive_feedback_grievance_ticket.language, "Polish, English")
            self.assertNotEqual(self.positive_feedback_grievance_ticket.area, "Example Town")
        else:
            self.assertEqual(self.positive_feedback_grievance_ticket.description, "")
            self.assertNotEqual(str(self.positive_feedback_grievance_ticket.assigned_to.id), self.user_two.id)
            self.assertEqual(self.positive_feedback_grievance_ticket.admin2, self.admin_area_2)
            self.assertEqual(self.positive_feedback_grievance_ticket.admin2_new, self.admin_area_2_new)
            self.assertEqual(self.positive_feedback_grievance_ticket.language, "Spanish")
            self.assertNotEqual(self.positive_feedback_grievance_ticket.area, "Example Town")

    @parameterized.expand(
        [
            (
                "SensitiveGrievanceTicket",
                SensitiveGrievanceTicketWithoutExtrasFactory,
            ),
            (
                "GrievanceComplaintTicket",
                GrievanceComplaintTicketWithoutExtrasFactory,
            ),
        ]
    )
    def test_set_household_if_not_set(self, _, factory):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        ticket = factory()
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        household, _ = create_household()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        household_id = self.id_to_base64(household.id, "HouseholdNode")

        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=self._prepare_input_data(ticket_id, household_id),
        )
        ticket.refresh_from_db()

        self.assertEqual(ticket.household, household)

    @parameterized.expand(
        [
            (
                "SensitiveGrievanceTicket",
                SensitiveGrievanceTicketWithoutExtrasFactory,
            ),
            (
                "GrievanceComplaintTicket",
                GrievanceComplaintTicketWithoutExtrasFactory,
            ),
        ]
    )
    def test_set_individual_if_not_set(self, _, factory):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        ticket = factory()
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        _, individuals = create_household()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        individual_id = self.id_to_base64(individuals[0].id, "IndividualNode")

        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=self._prepare_input_data(ticket_id, individual_id=individual_id),
        )
        ticket.refresh_from_db()

        self.assertEqual(ticket.individual, individuals[0])

    @parameterized.expand(
        [
            (
                "SensitiveGrievanceTicket",
                SensitiveGrievanceTicketWithoutExtrasFactory,
            ),
            (
                "GrievanceComplaintTicket",
                GrievanceComplaintTicketWithoutExtrasFactory,
            ),
        ]
    )
    def test_raise_exception_if_household_already_set(self, _, factory):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        household, _ = create_household()
        ticket = factory(household=self.household_one)
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        household_id = self.id_to_base64(household.id, "HouseholdNode")

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=self._prepare_input_data(ticket_id, household_id),
        )
        ticket.refresh_from_db()

        self.assertTrue("Cannot change household" in response["errors"][0]["message"])

    @parameterized.expand(
        [
            (
                "SensitiveGrievanceTicket",
                SensitiveGrievanceTicketWithoutExtrasFactory,
            ),
            (
                "GrievanceComplaintTicket",
                GrievanceComplaintTicketWithoutExtrasFactory,
            ),
        ]
    )
    def test_raise_exception_if_individual_already_set(self, _, factory):
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        household, individuals = create_household()
        ticket = factory(individual=individuals[1])
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        individual_id = self.id_to_base64(individuals[0].id, "IndividualNode")

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user},
            variables=self._prepare_input_data(ticket_id, individual_id=individual_id),
        )
        ticket.refresh_from_db()

        self.assertTrue("Cannot change individual" in response["errors"][0]["message"])

    def _prepare_input_data(self, ticket_id, household_id=None, individual_id=None):
        return {
            "input": {
                "description": "New Description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": self.admin_area_1_new.p_code,
                "language": "Polish, English",
                "area": "Example Town",
                "ticketId": ticket_id,
                "household": household_id,
                "individual": individual_id,
            }
        }
