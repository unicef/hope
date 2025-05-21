from datetime import date
from typing import Any

# from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.models import Partner
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import create_afghanistan
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import IDENTIFICATION_TYPE_TO_KEY_MAPPING
from hct_mis_api.apps.geo import models as geo_models
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory
from hct_mis_api.apps.household.fixtures import (
    DocumentFactory,
    HouseholdFactory,
    IndividualFactory,
    IndividualIdentityFactory,
)
from hct_mis_api.apps.household.models import (
    FEMALE,
    IDENTIFICATION_TYPE_CHOICE,
    IDENTIFICATION_TYPE_NATIONAL_ID,
    RELATIONSHIP_UNKNOWN,
    ROLE_NO_ROLE,
    SINGLE,
    UNHCR,
    WIDOWED,
    DocumentType,
)
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
        # program_different = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        country = geo_models.Country.objects.get(name="Afghanistan")
        area_type = AreaTypeFactory(
            name="Admin type one",
            country=country,
            area_level=2,
        )
        AreaFactory(name="City Test", area_type=area_type, p_code="dffgh565556")
        AreaFactory(name="City Example", area_type=area_type, p_code="fggtyjyj")

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

        country_pl = geo_models.Country.objects.get(iso_code2="PL")
        national_id_type = DocumentType.objects.get(
            key=IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID]
        )
        self.national_id = DocumentFactory.create(
            country=country_pl,
            id="d367e431-b807-4c1f-a811-ef2e0d217cc4",
            type=national_id_type,
            document_number="789-789-645",
            individual=self.individuals[0],
        )

        unhcr, _ = Partner.objects.get_or_create(name="UNHCR", defaults={"is_un": True})
        self.identity = IndividualIdentityFactory.create(
            id=1,
            partner=unhcr,
            individual=self.individuals[0],
            number="1111",
            country=country_pl,
        )

        area_type_level_1 = AreaTypeFactory(name="State1", area_level=1)
        self.area = AreaFactory(name="City Test1", area_type=area_type_level_1, p_code="area1")

        rebuild_search_index()

        self.list_url = reverse(
            "api:grievance:grievance-tickets-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
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
                            # "documents": [
                            #     {
                            #         "key": IDENTIFICATION_TYPE_TO_KEY_MAPPING[IDENTIFICATION_TYPE_NATIONAL_ID],
                            #         "country": "POL",
                            #         "number": "123-123-UX-321",
                            #         "photo": SimpleUploadedFile(name="test.jpg", content=b""),
                            #     }
                            # ],
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

        response = self.api_client.post(self.list_url, data, format="json")
        print("RESPONSE: ", response.json())
        assert response.status_code == status.HTTP_201_CREATED
