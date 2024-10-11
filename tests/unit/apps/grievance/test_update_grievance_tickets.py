from datetime import date
from typing import Any, Dict, List, Optional
from unittest import mock

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from factory import Factory
from parameterized import parameterized

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.base_test_case import APITestCase
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import (
    IDENTIFICATION_TYPE_TO_KEY_MAPPING,
    encode_id_base64,
)
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
    DocumentType,
    IndividualIdentity,
)
from hct_mis_api.apps.payment.delivery_mechanisms import DeliveryMechanismChoices
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import DeliveryMechanism
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.models import MergeStatusModel


class TestUpdateGrievanceTickets(APITestCase):
    fixtures = (f"{settings.PROJECT_ROOT}/apps/geo/fixtures/data.json",)

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
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        create_afghanistan()
        generate_delivery_mechanisms()
        cls.generate_document_types_for_all_countries()
        partner = PartnerFactory(name="Partner")
        cls.user = UserFactory(id="a5c44eeb-482e-49c2-b5ab-d769f83db116", partner=partner)
        cls.user_two = UserFactory(id="a34716d8-aaf1-4c70-bdd8-0d58be94981a")
        cls.business_area = BusinessArea.objects.get(slug="afghanistan")

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        cls.admin_area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="123333")
        cls.admin_area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="2343123")

        cls.program = ProgramFactory(
            name="Test program ONE", business_area=BusinessArea.objects.first(), status=Program.ACTIVE
        )
        cls.update_partner_access_to_program(partner, cls.program)

        household_one = HouseholdFactory.build(
            id="07a901ed-d2a5-422a-b962-3570da1d5d07", size=2, village="Example", program=cls.program
        )
        household_one.household_collection.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = cls.program
        household_one.registration_data_import.save()
        household_one.programs.add(cls.program)

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
            IndividualFactory(household=household_one, program=cls.program, **individual)
            for individual in cls.individuals_to_create
        ]

        first_individual = cls.individuals[0]
        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        birth_certificate_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )
        cls.national_id = DocumentFactory(
            country=country_pl,
            type=national_id_type,
            document_number="789-789-645",
            individual=first_individual,
            program=cls.program,
        )
        cls.birth_certificate = DocumentFactory(
            country=country_pl,
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=first_individual,
            program=cls.program,
        )
        household_one.head_of_household = cls.individuals[0]
        household_one.save()
        cls.household_one = household_one
        cls.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
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

        cls.individual_data_change_grievance_ticket = GrievanceTicketFactory(
            id="acd57aa1-efd8-4c81-ac19-b8cabebe8089",
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
                "relationship": RELATIONSHIP_UNKNOWN,
                "estimated_birth_date": False,
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": True},
                "role": {"value": ROLE_PRIMARY, "approve_status": True},
                "documents": [
                    {
                        "value": {
                            "country": "POL",
                            "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                            "number": "999-888-777",
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
        )
        PositiveFeedbackTicketWithoutExtrasFactory(ticket=cls.positive_feedback_grievance_ticket)

        unhcr, _ = Partner.objects.get_or_create(name="UNHCR", defaults={"is_un": True})
        cls.identity_to_update = IndividualIdentity.objects.create(
            partner=unhcr,
            individual=cls.individuals[0],
            number="1111",
            country=country_pl,
            rdi_merge_status=MergeStatusModel.MERGED,
        )

        cls.identity_to_remove = IndividualIdentity.objects.create(
            partner=unhcr,
            individual=cls.individuals[0],
            number="3456",
            country=country_pl,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        cls.dm_atm_card = DeliveryMechanism.objects.get(code="atm_card")
        cls.dmd = DeliveryMechanismDataFactory(
            individual=cls.individuals[0],
            delivery_mechanism=cls.dm_atm_card,
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
    def test_update_add_individual(self, name: str, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.add_individual_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.add_individual_grievance_ticket.save()
        input_data = {
            "input": {
                "description": self.add_individual_grievance_ticket.description,
                "assignedTo": self.id_to_base64(self.add_individual_grievance_ticket.assigned_to.id, "UserNode"),
                "admin": encode_id_base64(str(self.add_individual_grievance_ticket.admin2.id), "Area"),
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
                                    "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                    "country": "USA",
                                    "number": "321-321-UX-321",
                                    "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                }
                            ],
                            "identities": [
                                {
                                    "partner": UNHCR,
                                    "country": "POL",
                                    "number": "2222",
                                }
                            ],
                            "paymentChannels": [
                                {
                                    "type": "BANK_TRANSFER",
                                    "bankName": "privatbank",
                                    "bankAccountNumber": 2356789789789789,
                                    "accountHolderName": "Holder Name Updated",
                                    "bankBranchName": "Branch Name Updated",
                                },
                            ],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
        self.add_individual_grievance_ticket.refresh_from_db()
        result = self.add_individual_grievance_ticket.add_individual_ticket_details.individual_data
        # TODO: test shouldn't use conditional logic
        if name == "with_permission":
            expected_result = {
                "sex": "MALE",
                "role": "PRIMARY",
                "documents": [
                    {
                        "key": "national_id",
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
                        "account_holder_name": "Holder Name Updated",
                        "bank_branch_name": "Branch Name Updated",
                    },
                ],
                "identities": [{"partner": "UNHCR", "country": "POL", "number": "2222"}],
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
                "documents": [{"key": "national_id", "country": "POL", "number": "123-123-UX-321"}],
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
    def test_update_change_individual(self, name: str, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)
        self.individual_data_change_grievance_ticket.status = GrievanceTicket.STATUS_FOR_APPROVAL
        self.individual_data_change_grievance_ticket.save()
        input_data = {
            "input": {
                "description": self.individual_data_change_grievance_ticket.description,
                "assignedTo": self.id_to_base64(
                    self.individual_data_change_grievance_ticket.assigned_to.id, "UserNode"
                ),
                "admin": encode_id_base64(str(self.individual_data_change_grievance_ticket.admin2.id), "Area"),
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
                                    "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                    "number": "111-222-777",
                                    "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                                },
                            ],
                            "documentsToRemove": [],
                            "identities": [
                                {
                                    "partner": UNHCR,
                                    "country": "POL",
                                    "number": "2222",
                                }
                            ],
                            "identitiesToEdit": [
                                {
                                    "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                                    "partner": UNHCR,
                                    "country": "POL",
                                    "number": "3333",
                                }
                            ],
                            "deliveryMechanismDataToEdit": [
                                {
                                    "id": str(self.dmd.id),
                                    "label": DeliveryMechanismChoices.DELIVERY_TYPE_ATM_CARD,
                                    "approveStatus": False,
                                    "dataFields": [
                                        {"name": "phone_number", "value": "+1234567890"},
                                    ],
                                },
                            ],
                        }
                    }
                },
            }
        }
        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
        self.individual_data_change_grievance_ticket.refresh_from_db()
        result = self.individual_data_change_grievance_ticket.individual_data_update_ticket_details.individual_data
        expected_result: Dict
        # TODO: test shouldn't use conditional logic
        if name == "with_permission":
            expected_result = {
                "sex": {"value": "MALE", "approve_status": False, "previous_value": "FEMALE"},
                "role": {"value": "PRIMARY", "approve_status": False, "previous_value": "NO_ROLE"},
                "documents": [
                    {
                        "value": {
                            "key": "national_id",
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
                        "value": {"partner": "UNHCR", "number": "2222", "country": "POL"},
                        "approve_status": False,
                    },
                ],
                "identities_to_edit": [
                    {
                        "value": {
                            "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                            "partner": "UNHCR",
                            "number": "3333",
                            "country": "POL",
                            "individual": self.id_to_base64(self.individuals[0].id, "IndividualNode"),
                        },
                        "previous_value": {
                            "id": self.id_to_base64(self.identity_to_update.id, "IndividualIdentityNode"),
                            "partner": "UNHCR",
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
                "delivery_mechanism_data": [],
                "delivery_mechanism_data_to_edit": [
                    {
                        "id": str(self.dmd.id),
                        "label": self.dmd.delivery_mechanism.name,
                        "approve_status": False,
                        "data_fields": [
                            {
                                "name": "phone_number",
                                "value": "+1234567890",
                                "previous_value": None,
                            }
                        ],
                    }
                ],
                "delivery_mechanism_data_to_remove": [],
            }

        else:
            expected_result = {
                "sex": {"value": "MALE", "approve_status": False},
                "role": {"value": "PRIMARY", "approve_status": True},
                "documents": [
                    {
                        "value": {"key": "national_id", "number": "999-888-777", "country": "POL"},
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

    def test_update_change_household_with_permission(self) -> None:
        self.create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_UPDATE, Permissions.GRIEVANCES_UPDATE_REQUESTED_DATA_CHANGE],
            self.business_area,
        )

        input_data = {
            "input": {
                "description": "this is new description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": encode_id_base64(str(self.household_data_change_grievance_ticket.admin2.id), "Area"),
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
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
        self.household_data_change_grievance_ticket.refresh_from_db()
        result = self.household_data_change_grievance_ticket.household_data_update_ticket_details.household_data
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
        self.assertEqual(result, expected_result)
        self.assertEqual(str(self.household_data_change_grievance_ticket.assigned_to.id), self.user_two.id)
        self.assertNotEqual(self.household_data_change_grievance_ticket.description, "this is new description")
        self.assertEqual(self.household_data_change_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)

    def test_update_change_household_with_partial_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        input_data = {
            "input": {
                "description": "this is new description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": encode_id_base64(str(self.household_data_change_grievance_ticket.admin2.id), "Area"),
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
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
        self.household_data_change_grievance_ticket.refresh_from_db()
        result = self.household_data_change_grievance_ticket.household_data_update_ticket_details.household_data
        expected_result = {
            "village": {"value": "Test Village", "approve_status": True},
            "size": {"value": 19, "approve_status": True},
            "country": "AFG",
        }
        self.assertEqual(result, expected_result)
        self.assertEqual(str(self.household_data_change_grievance_ticket.assigned_to.id), self.user_two.id)
        self.assertNotEqual(self.household_data_change_grievance_ticket.description, "this is new description")
        self.assertEqual(self.household_data_change_grievance_ticket.status, GrievanceTicket.STATUS_IN_PROGRESS)

    def test_update_change_household_without_permission(self) -> None:
        self.create_user_role_with_permissions(self.user, [], self.business_area)

        input_data = {
            "input": {
                "description": "this is new description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": encode_id_base64(str(self.household_data_change_grievance_ticket.admin2.id), "Area"),
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
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )
        self.household_data_change_grievance_ticket.refresh_from_db()
        result = self.household_data_change_grievance_ticket.household_data_update_ticket_details.household_data
        expected_result = {
            "village": {"value": "Test Village", "approve_status": True},
            "size": {"value": 19, "approve_status": True},
            "country": "AFG",
        }
        self.assertEqual(result, expected_result)
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
    def test_update_feedback_ticket(self, name: str, permissions: List[Permissions]) -> None:
        self.create_user_role_with_permissions(self.user, permissions, self.business_area)

        input_data = {
            "input": {
                "description": "New Description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": encode_id_base64(str(self.admin_area_1.id), "Area"),
                "language": "Polish, English",
                "area": "Example Town",
                "ticketId": self.id_to_base64(self.positive_feedback_grievance_ticket.id, "GrievanceTicketNode"),
            }
        }
        self.snapshot_graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=input_data,
        )

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
    def test_set_household_if_not_set(self, _: Any, factory: Factory) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        ticket = factory()
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        household, _ = create_household()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        household_id = self.id_to_base64(household.id, "HouseholdNode")

        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_set_individual_if_not_set(self, _: Any, factory: Factory) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        ticket = factory()
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        _, individuals = create_household()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        individual_id = self.id_to_base64(individuals[0].id, "IndividualNode")

        self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_raise_exception_if_household_already_set(self, _: Any, factory: Factory) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        household, _ = create_household()
        ticket = factory(household=self.household_one)
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        household_id = self.id_to_base64(household.id, "HouseholdNode")

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
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
    def test_raise_exception_if_individual_already_set(self, _: Any, factory: Factory) -> None:
        self.create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.business_area)

        household, individuals = create_household()
        ticket = factory(individual=individuals[1])
        ticket.ticket.status = GrievanceTicket.STATUS_NEW
        ticket.ticket.save()
        ticket_id = self.id_to_base64(ticket.ticket.id, "GrievanceTicketNode")
        individual_id = self.id_to_base64(individuals[0].id, "IndividualNode")

        response = self.graphql_request(
            request_string=self.UPDATE_GRIEVANCE_TICKET_MUTATION,
            context={"user": self.user, "headers": {"Program": self.id_to_base64(self.program.id, "ProgramNode")}},
            variables=self._prepare_input_data(ticket_id, individual_id=individual_id),
        )
        ticket.refresh_from_db()

        self.assertTrue("Cannot change individual" in response["errors"][0]["message"])

    def _prepare_input_data(
        self, ticket_id: str, household_id: Optional[str] = None, individual_id: Optional[str] = None
    ) -> Dict:
        return {
            "input": {
                "description": "New Description",
                "assignedTo": self.id_to_base64(self.user_two.id, "UserNode"),
                "admin": encode_id_base64(str(self.admin_area_1.id), "Area"),
                "language": "Polish, English",
                "area": "Example Town",
                "ticketId": ticket_id,
                "household": household_id,
                "individual": individual_id,
            }
        }
