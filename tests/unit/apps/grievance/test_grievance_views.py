from datetime import date
from typing import Any

from django.core.management import call_command

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.grievance.fixtures import (
    GrievanceTicketFactory,
    TicketAddIndividualDetailsFactory,
    TicketHouseholdDataUpdateDetailsFactory,
    TicketIndividualDataUpdateDetailsFactory,
)
from hct_mis_api.apps.grievance.models import (
    GrievanceTicket,
    TicketAddIndividualDetails,
    TicketComplaintDetails,
    TicketDeleteHouseholdDetails,
    TicketDeleteIndividualDetails,
    TicketHouseholdDataUpdateDetails,
    TicketIndividualDataUpdateDetails,
)
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    RELATIONSHIP_UNKNOWN,
    ROLE_NO_ROLE,
    SINGLE,
    UNHCR,
    WIDOWED,
    DocumentType,
)
from hct_mis_api.apps.payment.fixtures import PaymentFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index

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

        self.program = ProgramFactory(
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

    def test_create_grievance_ticket_add_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_CREATE], self.afghanistan, self.program)
        data = {
            "description": "Test",
            "assigned_to": str(self.user.id),
            "issue_type": 16,
            "category": 2,
            "consent": True,
            "language": "PL",
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
                                    # "photo": SimpleUploadedFile(name="test_file.pdf", content=b"abc", content_type="application/pdf"),
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
        assert response.status_code == status.HTTP_201_CREATED
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


class TestGrievanceTicketUpdate:
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
        self.area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="fggtyjyj")

        self.program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )
        self.payment = PaymentFactory(
            parent__business_area=self.afghanistan, parent__program_cycle=self.program.cycles.first()
        )

        household_one = HouseholdFactory.build(size=3, country=country, program=self.program, unicef_id="HH-0001")
        household_one.household_collection.save()
        household_one.program.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()

        household_two = HouseholdFactory.build(program=self.program, unicef_id="HH-0002")
        household_two.household_collection.save()
        household_two.program.save()
        household_two.registration_data_import.imported_by.save()
        household_two.registration_data_import.program = household_two.program
        household_two.registration_data_import.save()

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
                household=household_one if index % 2 else household_two,
                program=household_one.program if index % 2 else household_two.program,
                **individual,
            )
            for index, individual in enumerate(self.individuals_to_create)
        ]
        household_one.head_of_household = self.individuals[0]
        household_two.head_of_household = self.individuals[1]
        household_one.save()
        household_two.save()
        self.household_one = household_one
        self.household_two = household_two

        area_type_level_1 = AreaTypeFactory(name="State1", area_level=1)
        self.area = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")

        rebuild_search_index()

        self.household_data_change_grievance_ticket = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=self.area,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_FOR_APPROVAL,
            created_by=self.user,
            assigned_to=self.user,
        )
        self.household_data_change_grievance_ticket.programs.set([self.program])
        self.household_data_change_grievance_ticket.save()
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grievance_ticket,
            household=self.household_one,
            household_data={
                "village": {"value": "Test Village", "approve_status": True},
                "size": {"value": 19, "approve_status": True},
                "country": "AFG",
            },
        )

        self.grv_2 = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_GRIEVANCE_COMPLAINT,
            issue_type=GrievanceTicket.ISSUE_TYPE_PAYMENT_COMPLAINT,
            admin2=self.area,
            business_area=self.afghanistan,
            status=GrievanceTicket.STATUS_IN_PROGRESS,
            created_by=self.user,
            assigned_to=self.user,
        )
        self.grv_2.programs.set([self.program])
        self.grv_2.save()

        TicketComplaintDetails.objects.create(
            ticket=self.grv_2,
            household=self.household_one,
            individual=self.individuals[0],
            payment=self.payment,
        )

        self.list_details = reverse(
            "api:grievance-tickets:grievance-tickets-global-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "pk": str(self.household_data_change_grievance_ticket.pk),
            },
        )

    def test_update_grievance_ticket_hh_update(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        data = {
            "description": "this is new description",
            "assigned_to": str(self.user.id),
            "admin": str(self.household_data_change_grievance_ticket.admin2.id),
            "language": self.household_data_change_grievance_ticket.language,
            "area": self.household_data_change_grievance_ticket.area,
            "extras": {
                "household_data_update_issue_type_extras": {
                    "household_data": {
                        "village": "Test New",
                        "size": 33,
                        "country": "AFG",
                    }
                }
            },
        }
        response = self.api_client.patch(self.list_details, data, format="json")
        resp_data = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert resp_data["ticket_details"]["household_data"]["village"]["value"] == "Test New"

    def test_update_grievance_ticket_complaint(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_UPDATE], self.afghanistan, self.program)
        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-detail",
            kwargs={"business_area_slug": self.afghanistan.slug, "pk": str(self.grv_2.pk)},
        )
        data = {
            "description": "AAAA",
            "assigned_to": str(self.user.id),
            "extras": {
                "category": {
                    "grievance_complaint_ticket_extras": {
                        "household": str(self.household_two.pk),
                        "individual": str(self.individuals[0].pk),
                        "payment_record": [str(self.payment.pk)],
                    }
                }
            },
        }
        response = self.api_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

    def test_grievance_status_change(self, create_user_role_with_permissions: Any) -> None:
        url = reverse(
            "api:grievance-tickets:grievance-tickets-global-status-change",
            kwargs={"business_area_slug": self.afghanistan.slug, "pk": str(self.grv_2.pk)},
        )
        create_user_role_with_permissions(
            self.user,
            [Permissions.GRIEVANCES_SET_IN_PROGRESS, Permissions.GRIEVANCES_SET_ON_HOLD],
            self.afghanistan,
            self.program,
        )
        response = self.api_client.post(url, {"status": 4}, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["status"] == 4

        # run one more time to be double sure and will have more coverage %
        response = self.api_client.post(url, {"status": 4}, format="json")
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert response.json()["status"] == 4

    def test_create_ticket_note(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.GRIEVANCES_ADD_NOTE], self.afghanistan, self.program)
        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-create-note",
                kwargs={"business_area_slug": self.afghanistan.slug, "pk": str(self.grv_2.pk)},
            ),
            {"version": self.grv_2.version, "description": "test new note"},
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in resp_data
        assert resp_data["description"] == "test new note"


class TestGrievanceTicketApprove:
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
        # program_different = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        self.area_1 = AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")
        self.area_2 = AreaFactory(name="City Example", area_type=area_type, p_code="fggtyjyj")

        self.program = ProgramFactory(
            status=Program.ACTIVE,
            business_area=BusinessArea.objects.first(),
        )
        self.payment = PaymentFactory(
            parent__business_area=self.afghanistan, parent__program_cycle=self.program.cycles.first()
        )

        household_one = HouseholdFactory.build(size=3, country=country, program=self.program, unicef_id="HH-0001")
        household_one.household_collection.save()
        household_one.program.save()
        household_one.registration_data_import.imported_by.save()
        household_one.registration_data_import.program = household_one.program
        household_one.registration_data_import.save()

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

        self.individuals = [
            IndividualFactory(household=household_one, program=self.program, **individual)
            for individual in self.individuals_to_create
        ]
        first_individual = self.individuals[0]
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        birth_certificate_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_BIRTH_CERTIFICATE]
        )
        country_pol = geo_models.Country.objects.get(iso_code2="PL")

        self.national_id = DocumentFactory(
            id="df1ce6e8-2864-4c3f-803d-19ec6f4c47f3",
            type=national_id_type,
            document_number="789-789-645",
            individual=first_individual,
            country=country_pol,
        )
        self.birth_certificate = DocumentFactory(
            id="8ad5e3b8-4c4d-4c10-8756-118d86095dd0",
            type=birth_certificate_type,
            document_number="ITY8456",
            individual=first_individual,
            country=country_pol,
        )
        household_one.head_of_household = first_individual
        household_one.save()
        self.household_one = household_one

        self.add_individual_grievance_ticket = GrievanceTicketFactory(
            id="43c59eda-6664-41d6-9339-05efcb11da82",
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_DATA_CHANGE_ADD_INDIVIDUAL,
            admin2=self.area_1,
            business_area=self.afghanistan,
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
                "documents": [
                    {
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                        "number": "123-XYZ-321",
                    },
                    {
                        "country": "POL",
                        "type": IDENTIFICATION_TYPE_BIRTH_CERTIFICATE,
                        "number": "QWE4567",
                    },
                ],
            },
            approve_status=False,
        )

        self.individual_data_change_grv = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_INDIVIDUAL_DATA_CHANGE_DATA_UPDATE,
            admin2=self.area_1,
            business_area=self.afghanistan,
        )
        self.individual_data_change_grv.programs.set([self.program])
        self.individual_data_change_grv.save()
        TicketIndividualDataUpdateDetailsFactory(
            ticket=self.individual_data_change_grv,
            individual=self.individuals[0],
            individual_data={
                "given_name": {"value": "Test", "approve_status": False},
                "full_name": {"value": "Test Example", "approve_status": False},
                "family_name": {"value": "Example", "approve_status": False},
                "sex": {"value": "MALE", "approve_status": False},
                "birth_date": {"value": date(year=1980, month=2, day=1).isoformat(), "approve_status": False},
                "marital_status": {"value": SINGLE, "approve_status": False},
                "documents": [
                    {
                        "value": {"country": "POL", "type": IDENTIFICATION_TYPE_NATIONAL_ID, "number": "999-888-777"},
                        "approve_status": False,
                    },
                ],
                "documents_to_edit": [
                    {
                        "value": {
                            "id": self.national_id.id,
                            "country": None,
                            "type": None,
                            "number": "999-888-666",
                            "photo": "",
                        },
                        "previous_value": {
                            "id": self.national_id.id,
                            "country": "POL",
                            "type": IDENTIFICATION_TYPE_NATIONAL_ID,
                            "number": "789-789-645",
                            "photo": "",
                        },
                        "approve_status": False,
                    }
                ],
                "documents_to_remove": [
                    {"value": self.national_id.id, "approve_status": False},
                    {"value": self.birth_certificate.id, "approve_status": False},
                ],
                "flex_fields": {},
            },
        )

        self.household_data_change_grv = GrievanceTicketFactory(
            category=GrievanceTicket.CATEGORY_DATA_CHANGE,
            issue_type=GrievanceTicket.ISSUE_TYPE_HOUSEHOLD_DATA_CHANGE_DATA_UPDATE,
            admin2=self.area_1,
            business_area=self.afghanistan,
        )
        self.household_data_change_grv.programs.set([self.program])
        self.household_data_change_grv.save()
        TicketHouseholdDataUpdateDetailsFactory(
            ticket=self.household_data_change_grv,
            household=self.household_one,
            household_data={
                "village": {"value": "Test Village"},
                "size": {"value": 19},
                "flex_fields": {},
            },
        )

    def test_approve_individual_data_change(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            self.user, [Permissions.GRIEVANCES_APPROVE_DATA_CHANGE], self.afghanistan, self.program
        )
        data = {
            "individual_approve_data": {"given_name": True, "full_name": True, "family_name": True},
            "approved_documents_to_create": [0],
            "approved_documents_to_edit": [0],
            "approved_documents_torRemove": [0],
            "approved_identities_to_create": [],
            "approved_identities_to_edit": [],
            "approved_identities_to_remove": [],
            "approved_payment_channels_to_create": [],
            "approved_payment_channels_to_edit": [],
            "approved_payment_channels_to_remove": [],
            "flex_fields_approve_data": {},
        }
        response = self.api_client.post(
            reverse(
                "api:grievance-tickets:grievance-tickets-global-approve-individual-data-change",
                kwargs={"business_area_slug": self.afghanistan.slug, "pk": str(self.individual_data_change_grv.pk)},
            ),
            data,
            format="json",
        )
        resp_data = response.json()
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "id" in resp_data
