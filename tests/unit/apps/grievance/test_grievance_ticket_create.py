from datetime import date
from typing import Any

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

import pytest
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory
from extras.test_utils.factories.household import HouseholdFactory, IndividualFactory
from extras.test_utils.factories.payment import PaymentFactory
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.core.models import BusinessArea
from hope.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hope.apps.geo import models as geo_models
from hope.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
)
from hope.apps.household.models import (
    FEMALE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    RELATIONSHIP_UNKNOWN,
    ROLE_ALTERNATE,
    ROLE_NO_ROLE,
    ROLE_PRIMARY,
    SINGLE,
    UNHCR,
    WIDOWED,
    DocumentType,
    IndividualRoleInHousehold,
)
from hope.apps.program.models import Program
from hope.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.django_db()


class TestGrievanceTicketCreate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        call_command("loadcountries")
        self.afghanistan = create_afghanistan()
        # generate document types
        identification_type_choice = tuple((doc_type, label) for doc_type, label in IDENTIFICATION_TYPE_CHOICE)
        document_types = []
        for doc_type, label in identification_type_choice:
            document_types.append(DocumentType(label=label, key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[doc_type]))
        DocumentType.objects.bulk_create(document_types, ignore_conflicts=True)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.user2 = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")

        self.program_2 = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )

        household_one = HouseholdFactory.build(size=3, country=country, program=self.program, unicef_id="HH-0001")
        household_one.household_collection.save()
        household_one.program.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()

        self.individuals_to_create = [
            {
                "id": "b6ffb227-a2dd-4103-be46-0c9ebe9f001a",
                "full_name": "Benjamin Butler",
                "given_name": "Benjamin",
                "family_name": "Butler",
                "phone_no": "(953)682-4596",
                "birth_date": "1943-07-30",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "e6b0acc8-f4db-4d70-8f50-c2080b3ba9ec",
                "full_name": "Robin Ford",
                "given_name": "Robin",
                "family_name": "Ford",
                "phone_no": "+18663567905",
                "birth_date": "1946-02-15",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "667be49c-6620-4381-a69a-211ba9f7d8c8",
                "full_name": "Timothy Perry",
                "given_name": "Timothy",
                "family_name": "Perry",
                "phone_no": "(548)313-1700-902",
                "birth_date": "1983-12-21",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "ef52d4d7-3142-4d51-a31b-2ad231120c58",
                "full_name": "Eric Torres",
                "given_name": "Eric",
                "family_name": "Torres",
                "phone_no": "(228)231-5473",
                "birth_date": "1973-03-23",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
            {
                "id": "cb2e2e3a-d9c4-40ce-8777-707ca18d7fc8",
                "full_name": "Jenna Franklin",
                "given_name": "Jenna",
                "family_name": "Franklin",
                "phone_no": "001-296-358-5428-607",
                "birth_date": "1969-11-29",
                "sex": FEMALE,
                "marital_status": WIDOWED,
                "estimated_birth_date": False,
                "relationship": RELATIONSHIP_UNKNOWN,
            },
        ]
        self.individuals = [
            IndividualFactory(
                household=household_one,
                program=household_one.program,
                **individual,
            )
            for individual in self.individuals_to_create
        ]
        household_one.head_of_household = self.individuals[0]
        household_one.save()
        self.household_one = household_one

        self.list_url = reverse(
            "api:grievance-tickets:grievance-tickets-global-list",
            kwargs={"business_area_slug": self.afghanistan.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status", "create_perm_for_program"),
        [
            ([Permissions.GRIEVANCES_CREATE], status.HTTP_201_CREATED, True),
            ([], status.HTTP_403_FORBIDDEN, True),
            ([Permissions.GRIEVANCES_CREATE], status.HTTP_403_FORBIDDEN, False),
        ],
    )
    def test_create_grievance_ticket_add_individual(
        self,
        permissions: list,
        expected_status: int,
        create_perm_for_program: bool,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            self.user, permissions, self.afghanistan, self.program if create_perm_for_program else self.program_2
        )
        data = {
            "description": "Test",
            "assigned_to": str(self.user.id),
            "issue_type": 16,
            "category": 2,
            "consent": True,
            "language": "PL",
            "program": str(self.program.pk),
            "documentation": [],
            "extras": {
                "issue_type": {
                    "add_individual_issue_type_extras": {
                        "household": str(self.household_one.id),
                        "individual_data": {
                            "given_name": "Test",
                            "full_name": "Test Test",
                            "family_name": "Romaniak",
                            "sex": "MALE",
                            "birth_date": date(year=1980, month=2, day=1).isoformat(),
                            "marital_status": SINGLE,
                            "estimated_birth_date": False,
                            "relationship": RELATIONSHIP_UNKNOWN,
                            "role": ROLE_NO_ROLE,
                            "documents": [
                                {
                                    "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                                    "country": "POL",
                                    "number": "123-123-UX-321",
                                }
                            ],
                            "identities": [
                                {
                                    "partner": UNHCR,
                                    "country": "POL",
                                    "number": "2222",
                                }
                            ],
                            "payment_channels": [
                                {
                                    "type": "BANK_TRANSFER",
                                    "bank_name": "privatbank",
                                    "bank_account_number": 2356789789789789,
                                    "account_holder_name": "Holder Name 132",
                                    "bank_branch_name": "newName 123",
                                },
                            ],
                        },
                    }
                }
            },
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketAddIndividualDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()

        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert len(resp_data) == 1
            assert GrievanceTicket.objects.all().count() == 1
            assert TicketAddIndividualDetails.objects.all().count() == 1

    def test_create_grievance_ticket_update_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Description upd HH",
            "language": "Polish",
            "area": str(self.area_1.pk),
            "issue_type": 13,
            "category": 2,
            "consent": True,
            "extras": {
                "issue_type": {
                    "household_data_update_issue_type_extras": {
                        "household": str(self.household_one.id),
                        "household_data": {
                            "village": "Test Town",
                            "size": 3,
                            "country": "AFG",
                        },
                    }
                },
            },
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketHouseholdDataUpdateDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketHouseholdDataUpdateDetails.objects.all().count() == 1

    def test_create_grievance_ticket_update_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Upd Ind",
            "language": "Polish",
            "area": str(self.area_1.pk),
            "issue_type": 14,
            "category": 2,
            "consent": True,
            "extras": {
                "issue_type": {
                    "individual_data_update_issue_type_extras": {
                        "individual": str(self.individuals[0].pk),
                        "individual_data": {
                            "full_name": "New full_name",
                        },
                    }
                },
            },
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketIndividualDataUpdateDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketIndividualDataUpdateDetails.objects.all().count() == 1

    def test_create_grievance_ticket_update_individual_with_document(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_CREATE, Permissions.GRIEVANCE_DOCUMENTS_UPLOAD],
            self.afghanistan,
            self.program,
        )
        fake_file = SimpleUploadedFile("test.jpeg", b"test file content", content_type="image/jpeg")
        data = {
            "description": "Upd Ind",
            "language": "Polish",
            "area": str(self.area_1.pk),
            "issue_type": 14,
            "category": 2,
            "consent": True,
            "extras.issue_type.individual_data_update_issue_type_extras.individual": str(self.individuals[0].pk),
            "extras.issue_type.individual_data_update_issue_type_extras.individual_data.full_name": "New full_name",
            "documentation[0].file": fake_file,
            "documentation[0].name": fake_file.name,
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketIndividualDataUpdateDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="multipart")
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketIndividualDataUpdateDetails.objects.all().count() == 1
        assert GrievanceTicket.objects.first().support_documents.count() == 1

    def test_create_grievance_ticket_delete_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Delete Ind",
            "language": "Polish",
            "area": str(self.area_1.pk),
            "issue_type": 15,
            "category": 2,
            "consent": True,
            "extras": {
                "issue_type": {
                    "individual_delete_issue_type_extras": {
                        "individual": str(self.individuals[0].pk),
                    }
                },
            },
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketDeleteIndividualDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketDeleteIndividualDetails.objects.all().count() == 1

    def test_create_grievance_ticket_delete_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Remove HH",
            "language": "Polish",
            "area": str(self.area_1.pk),
            "issue_type": 17,
            "category": 2,
            "consent": True,
            "extras": {
                "issue_type": {
                    "household_delete_issue_type_extras": {
                        "household": str(self.household_one.pk),
                    }
                },
            },
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketDeleteHouseholdDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketDeleteHouseholdDetails.objects.all().count() == 1

    def test_create_grievance_ticket_complaint(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        payment = PaymentFactory(
            household=self.household_one,
            collector=self.individuals[0],
            business_area=self.afghanistan,
            currency="PLN",
            parent__created_by=self.user,
        )
        data = {
            "description": "Test Feedback",
            "category": GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
            "language": "Polish, English",
            "consent": True,
            "extras": {
                "category": {
                    "grievance_complaint_ticket_extras": {
                        "household": str(self.household_one.pk),
                        "individual": str(self.individuals[0].pk),
                        "payment_record": [str(payment.pk)],
                    }
                }
            },
        }

        assert GrievanceTicket.objects.all().count() == 0
        assert TicketComplaintDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert len(resp_data) == 1
        assert GrievanceTicket.objects.all().count() == 1
        assert TicketComplaintDetails.objects.all().count() == 1

    def test_create_grievance_ticket_validation_errors(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Test Feedback",
            "category": GrievanceTicket.CATEGORY_NEGATIVE_FEEDBACK,
            "issue_type": GrievanceTicket.ISSUE_TYPE_FSP_COMPLAINT,
            "language": "Polish, English",
            "consent": True,
            "extras": {},
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketComplaintDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Feedback tickets are not allowed to be created through this mutation." in response.json()

    def test_create_grievance_ticket_duplicate_roles_not_allowed(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        individual = IndividualFactory(program=self.program)
        household = individual.household
        individual_2 = IndividualFactory(program=self.program, household=household)
        IndividualRoleInHousehold.objects.create(
            household=household,
            individual=individual,
            role=ROLE_ALTERNATE,
            rdi_merge_status=MergeStatusModel.MERGED,
        )
        extras = {
            "issue_type": {
                "household_data_update_issue_type_extras": {
                    "household": str(household.pk),
                    "household_data": {
                        "village": "New Village",
                        "country": "AGO",
                        "flex_fields": {},
                        "roles": [
                            {"individual": str(individual.pk), "new_role": ROLE_PRIMARY},
                            {"individual": str(individual_2.pk), "new_role": ROLE_PRIMARY},
                        ],
                    },
                }
            }
        }
        input_data = {
            "description": "Test update roles",
            "category": GrievanceTicket.CATEGORY_DATA_CHANGE,
            "consent": False,
            "language": "",
            "linked_feedback_id": None,
            "issue_type": GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            "extras": extras,
        }
        assert GrievanceTicket.objects.all().count() == 0
        assert TicketComplaintDetails.objects.all().count() == 0
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert (
            f"Duplicate roles are not allowed: {ROLE_PRIMARY}"
            in response.json()["extras"]["issue_type"]["household_data_update_issue_type_extras"]["household_data"][
                "roles"
            ]
        )
        # coverage
        extras["issue_type"]["household_data_update_issue_type_extras"]["household_data"]["roles"] = [
            {"individual": str(individual.pk), "new_role": ROLE_PRIMARY},
            {"individual": str(individual_2.pk), "new_role": ROLE_ALTERNATE},
        ]
        response = self.api_client.post(self.list_url, input_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
