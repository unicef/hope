import json
from typing import Any, Dict, List, Optional, Tuple

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import freezegun
import pytest
from constance.test import override_config
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    create_ukraine,
)
from hct_mis_api.apps.core.models import PeriodicFieldData
from hct_mis_api.apps.core.utils import encode_id_base64_required
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.household.fixtures import (
    BankAccountInfoFactory,
    DocumentFactory,
    DocumentTypeFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from hct_mis_api.apps.household.models import (
    CANNOT_DO,
    DISABLED,
    DUPLICATE,
    FEMALE,
    HEARING,
    LOT_DIFFICULTY,
    MALE,
    NEEDS_ADJUDICATION,
    NOT_COLLECTED,
    OTHER,
    ROLE_ALTERNATE,
    ROLE_PRIMARY,
    SEEING,
    STATUS_ACTIVE,
    UNIQUE,
    DocumentType,
    Household,
    Individual,
)
from hct_mis_api.apps.payment.fixtures import (
    DeliveryMechanismDataFactory,
    generate_delivery_mechanisms,
)
from hct_mis_api.apps.payment.models import AccountType
from hct_mis_api.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from hct_mis_api.apps.registration_data.fixtures import RegistrationDataImportFactory
from hct_mis_api.apps.utils.elasticsearch_utils import rebuild_search_index
from hct_mis_api.apps.utils.models import MergeStatusModel

pytestmark = pytest.mark.django_db()


def get_encoded_individual_id(individual: Individual) -> str:
    return encode_id_base64_required(individual.id, "Individual")


def get_encoded_household_id(household: Household) -> str:
    return encode_id_base64_required(household.id, "Household")


class TestIndividualList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        different_program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:households:individuals-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )
        self.count_url = reverse(
            "api:households:individuals-count",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=admin_type_1)

        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)

        self.household1, (self.individual1_1, self.individual1_2) = self._create_household(self.program)
        self.household2, (self.individual2_1, self.individual2_2) = self._create_household(self.program)
        self.household_from_different_program, (
            self.individual_from_different_program_1,
            self.individual_from_different_program_2,
        ) = self._create_household(different_program)

    def _create_household(self, program: Program) -> tuple[Household, List[Individual]]:
        household, individuals = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "program": program,
                "business_area": self.afghanistan,
            },
            individuals_data=[
                {
                    "program": program,
                    "business_area": self.afghanistan,
                },
                {
                    "program": program,
                    "business_area": self.afghanistan,
                },
            ],
        )

        return household, individuals

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_individual_list_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.list_url)
        assert response.status_code == expected_status

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_individual_count(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.count_url)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_200_OK:
            assert response.json()["count"] == 4

    def test_individuals_list(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()["results"]
        assert len(response_results) == 4

        response_count = self.api_client.get(self.count_url)
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 4

        response_ids = [result["id"] for result in response_results]
        assert get_encoded_individual_id(self.individual1_1) in response_ids
        assert get_encoded_individual_id(self.individual1_2) in response_ids
        assert get_encoded_individual_id(self.individual2_1) in response_ids
        assert get_encoded_individual_id(self.individual2_2) in response_ids

        for i, individual in enumerate(
            [self.individual1_1, self.individual1_2, self.individual2_1, self.individual2_2]
        ):
            individual_result = response_results[i]
            assert individual_result["id"] == get_encoded_individual_id(individual)
            assert individual_result["unicef_id"] == individual.unicef_id
            assert individual_result["full_name"] == individual.full_name
            assert individual_result["status"] == individual.status
            assert individual_result["relationship"] == individual.relationship
            assert individual_result["age"] == individual.age
            assert individual_result["sex"] == individual.sex
            assert individual_result["household"] == {
                "id": get_encoded_household_id(individual.household),
                "unicef_id": individual.household.unicef_id,
                "admin2": individual.household.admin2.name,
            }

    def test_individual_list_on_draft_program(self, create_user_role_with_permissions: Any) -> None:
        program = ProgramFactory(business_area=self.afghanistan, status=Program.DRAFT)
        list_url = reverse(
            "api:households:individuals-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": program.slug},
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=program,
        )
        for _ in range(2):
            self._create_household(program)

        response = self.api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 0

    def test_individual_list_with_admin_area_limits(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])

        household_without_areas, (
            individual_without_areas1,
            individual_without_areas2,
        ) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.area1.area_type)
        household_different_areas, (individual_different_areas1, individual_different_areas2) = self._create_household(
            self.program
        )
        household_different_areas.admin1 = area_different
        household_different_areas.admin2 = area_different
        household_different_areas.save()

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 6

        response_ids = [result["id"] for result in response_results]
        assert get_encoded_individual_id(self.individual1_1) in response_ids
        assert get_encoded_individual_id(self.individual1_2) in response_ids
        assert get_encoded_individual_id(self.individual2_1) in response_ids
        assert get_encoded_individual_id(self.individual2_2) in response_ids
        assert get_encoded_individual_id(individual_without_areas1) in response_ids
        assert get_encoded_individual_id(individual_without_areas2) in response_ids
        assert get_encoded_individual_id(individual_different_areas1) not in response_ids
        assert get_encoded_individual_id(individual_different_areas2) not in response_ids

    def test_individual_list_caching(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )

        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 4
            assert len(ctx.captured_queries) == 21

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 10

        self.individual1_1.given_name = "Jane"
        self.individual1_1.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_third_call = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            # 5 queries are saved because of cached permissions calculations
            assert len(ctx.captured_queries) == 16

        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_changed_areas = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert etag_changed_areas not in [etag, etag_second_call, etag_third_call]
            assert len(ctx.captured_queries) == 16

        self.individual1_1.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert len(response.json()["results"]) == 3
            assert etag_fourth_call not in [etag, etag_second_call, etag_third_call, etag_changed_areas]
            assert len(ctx.captured_queries) == 15

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 10


class TestIndividualDetail:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.detail_url_name = "api:households:individuals-detail"

        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=admin_type_1)

        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)
        self.area3 = AreaFactory(parent=self.area2, p_code="AF010101", area_type=admin_type_2)
        self.area4 = AreaFactory(parent=self.area3, p_code="AF01010101", area_type=admin_type_2)

        self.registration_data_import = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        self.household, (self.individual1, self.individual2) = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "country": self.country,
                "country_origin": self.country,
                "program": self.program,
                "business_area": self.afghanistan,
                "registration_data_import": self.registration_data_import,
            },
            individuals_data=[
                {
                    "pregnant": True,
                    "observed_disability": [SEEING, HEARING],
                    "seeing_disability": LOT_DIFFICULTY,
                    "hearing_disability": CANNOT_DO,
                    "disability": DISABLED,
                },
                {},
            ],
        )

        self.household2, _ = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        # self.individual1 is PRIMARY collector in self.household and ALTERNATE in self.household2
        self.role_primary = IndividualRoleInHouseholdFactory(
            individual=self.individual1,
            household=self.household,
            role=ROLE_PRIMARY,
        )
        self.role_alternate = IndividualRoleInHouseholdFactory(
            individual=self.individual1,
            household=self.household2,
            role=ROLE_ALTERNATE,
        )

        self.individual1.deduplication_golden_record_status = DUPLICATE
        self.individual1.duplicate = True
        self.individual1.save()

        # linked tickets
        self.grievance_ticket = GrievanceTicketFactory(household_unicef_id=self.household.unicef_id)
        GrievanceTicketFactory()  # not linked ticket

        # flex fields
        self.individual1.flex_fields = {
            "wellbeing_index_i_f": 24,
            "school_enrolled_before_i_f": 1,
        }
        pdu_data1 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.DECIMAL,
            number_of_rounds=3,
            rounds_names=["Round 1", "Round 2", "Round 3"],
        )
        FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field 1",
            pdu_data=pdu_data1,
        )
        pdu_data_2 = PeriodicFieldDataFactory(
            subtype=PeriodicFieldData.STRING,
            number_of_rounds=4,
            rounds_names=["Round A", "Round B", "Round C", "Round D"],
        )
        FlexibleAttributeForPDUFactory(
            program=self.program,
            label="PDU Field 2",
            pdu_data=pdu_data_2,
        )
        self.individual1.flex_fields = populate_pdu_with_null_values(self.program, self.individual1.flex_fields)
        # populate some values - in the response only populated values should be returned
        self.individual1.flex_fields["pdu_field_1"]["1"] = {
            "value": 123.45,
            "collection_date": "2021-01-01",
        }
        self.individual1.flex_fields["pdu_field_1"]["2"] = {
            "value": 234.56,
            "collection_date": "2021-01-01",
        }
        self.individual1.flex_fields["pdu_field_2"]["4"] = {
            "value": "Value D",
            "collection_date": "2021-01-01",
        }
        self.individual1.save()

        # documents
        self.national_id_type = DocumentTypeFactory(key="national_id")
        self.national_passport_type = DocumentTypeFactory(key="national_passport")
        self.tax_id_type = DocumentTypeFactory(key="tax_id")
        self.birth_certificate_type = DocumentTypeFactory(key="birth_certificate")
        self.disability_card_type = DocumentTypeFactory(key="disability_card")
        self.drivers_license_type = DocumentTypeFactory(key="drivers_license")

        self.national_id = DocumentFactory(
            document_number="123-456-789",
            type=DocumentType.objects.get(key="national_id"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
        )

        self.national_passport = DocumentFactory(
            document_number="111-222-333",
            type=DocumentTypeFactory(key="national_passport"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
        )

        self.birth_certificate = DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="birth_certificate"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
        )

        self.disability_card = DocumentFactory(
            document_number="10000000000",
            type=DocumentType.objects.get(key="disability_card"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
        )

        self.drivers_license = DocumentFactory(
            document_number="1234567890",
            type=DocumentType.objects.get(key="drivers_license"),
            individual=self.individual1,
            program=self.program,
        )

        self.tax_id = DocumentFactory(
            document_number="666-777-888",
            type=DocumentType.objects.get(key="tax_id"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
        )

        # bank account info
        self.bank_account_info = BankAccountInfoFactory(
            individual=self.individual1,
            bank_name="ING",
            bank_account_number=11110000222255558888999925,
        )

        # identity
        self.identity = IndividualIdentityFactory(
            country=self.country,
            individual=self.individual1,
        )

        # delivery mechanisms data
        generate_delivery_mechanisms()
        self.account_type_bank = AccountType.objects.get(key="bank")
        self.dm_atm_card_data = DeliveryMechanismDataFactory(
            individual=self.individual1,
            account_type=self.account_type_bank,
            data={
                "card_number": "123",
                "card_expiry_date": "2022-01-01",
                "name_of_cardholder": "Marek",
            },
        )
        self.account_type_mobile = AccountType.objects.get(key="bank")
        self.dm_mobile_money_data = DeliveryMechanismDataFactory(
            individual=self.individual1,
            account_type=self.account_type_mobile,
            data={
                "service_provider_code": "ABC",
                "delivery_phone_number": "123456789",
                "provider": "Provider",
            },
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS], status.HTTP_200_OK),
            ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_individual_detail_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        encoded_individual_id = get_encoded_individual_id(self.individual1)
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": encoded_individual_id,
                },
            )
        )
        assert response.status_code == expected_status

    def test_individual_detail(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
                Permissions.POPULATION_VIEW_INDIVIDUAL_DELIVERY_MECHANISMS_SECTION,
            ],
            business_area=self.afghanistan,
            program=self.program,
        )
        encoded_individual_id = get_encoded_individual_id(self.individual1)
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": encoded_individual_id,
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        assert data["id"] == encoded_individual_id
        assert data["unicef_id"] == self.individual1.unicef_id
        assert data["full_name"] == self.individual1.full_name
        assert data["given_name"] == self.individual1.given_name
        assert data["middle_name"] == self.individual1.middle_name
        assert data["family_name"] == self.individual1.family_name
        assert data["sex"] == self.individual1.sex
        assert data["age"] == self.individual1.age
        assert data["birth_date"] == f"{self.individual1.birth_date:%Y-%m-%d}"
        assert data["estimated_birth_date"] == self.individual1.estimated_birth_date
        assert data["marital_status"] == self.individual1.marital_status
        assert data["work_status"] == self.individual1.work_status
        assert data["pregnant"] == self.individual1.pregnant
        assert data["household"] == {
            "id": get_encoded_household_id(self.individual1.household),
            "unicef_id": self.individual1.household.unicef_id,
            "admin2": self.individual1.household.admin2.name,
        }
        assert data["role"] == ROLE_PRIMARY
        assert data["relationship"] == self.individual1.relationship
        assert data["registration_data_import"] == {
            "id": encode_id_base64_required(self.registration_data_import.id, "RegistrationDataImport"),
            "name": self.registration_data_import.name,
            "status": self.registration_data_import.status,
            "import_date": f"{self.registration_data_import.import_date:%Y-%m-%dT%H:%M:%S.%fZ}",
            "number_of_individuals": self.registration_data_import.number_of_individuals,
            "number_of_households": self.registration_data_import.number_of_households,
            "imported_by": {
                "first_name": self.registration_data_import.imported_by.first_name,
                "last_name": self.registration_data_import.imported_by.last_name,
                "email": self.registration_data_import.imported_by.email,
                "username": self.registration_data_import.imported_by.username,
            },
            "data_source": self.registration_data_import.data_source,
        }
        assert data["import_id"] == self.individual1.unicef_id
        assert data["preferred_language"] == self.individual1.preferred_language
        assert data["roles_in_households"] == [
            {
                "id": encode_id_base64_required(self.role_primary.id, "IndividualRoleInHousehold"),
                "household": {
                    "id": encode_id_base64_required(self.household.id, "Household"),
                    "unicef_id": self.household.unicef_id,
                    "admin2": self.household.admin2.name,
                },
                "role": ROLE_PRIMARY,
            },
            {
                "id": encode_id_base64_required(self.role_alternate.id, "IndividualRoleInHousehold"),
                "household": {
                    "id": encode_id_base64_required(self.household2.id, "Household"),
                    "unicef_id": self.household2.unicef_id,
                    "admin2": "",
                },
                "role": ROLE_ALTERNATE,
            },
        ]
        assert data["observed_disability"] == self.individual1.observed_disability
        assert data["seeing_disability"] == self.individual1.seeing_disability
        assert data["hearing_disability"] == self.individual1.hearing_disability
        assert data["physical_disability"] == self.individual1.physical_disability
        assert data["memory_disability"] == self.individual1.memory_disability
        assert data["selfcare_disability"] == self.individual1.selfcare_disability
        assert data["comms_disability"] == self.individual1.comms_disability
        assert data["disability"] == self.individual1.disability
        assert data["email"] == self.individual1.email
        assert data["phone_no"] == self.individual1.phone_no
        assert data["phone_no_alternative"] == self.individual1.phone_no_alternative
        assert data["sanction_list_last_check"] == self.individual1.sanction_list_last_check
        assert data["wallet_name"] == self.individual1.wallet_name
        assert data["blockchain_name"] == self.individual1.blockchain_name
        assert data["wallet_address"] == self.individual1.wallet_address
        assert data["status"] == self.individual1.status

        assert data["flex_fields"] == {
            "wellbeing_index_i_f": 24,
            "school_enrolled_before_i_f": 1,
            "pdu_field_1": {
                "1": {"collection_date": "2021-01-01", "value": 123.45},
                "2": {"collection_date": "2021-01-01", "value": 234.56},
            },
            "pdu_field_2": {"4": {"collection_date": "2021-01-01", "value": "Value D"}},
        }

        assert data["documents"] == [
            {
                "id": encode_id_base64_required(self.national_id.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.national_id_type.id, "DocumentType"),
                    "label": self.national_id_type.label,
                    "key": self.national_id_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.national_id.document_number,
            },
            {
                "id": encode_id_base64_required(self.national_passport.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.national_passport_type.id, "DocumentType"),
                    "label": self.national_passport_type.label,
                    "key": self.national_passport_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.national_passport.document_number,
            },
            {
                "id": encode_id_base64_required(self.birth_certificate.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.birth_certificate_type.id, "DocumentType"),
                    "label": self.birth_certificate_type.label,
                    "key": self.birth_certificate_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.birth_certificate.document_number,
            },
            {
                "id": encode_id_base64_required(self.disability_card.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.disability_card_type.id, "DocumentType"),
                    "label": self.disability_card_type.label,
                    "key": self.disability_card_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.disability_card.document_number,
            },
            {
                "id": encode_id_base64_required(self.drivers_license.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.drivers_license_type.id, "DocumentType"),
                    "label": self.drivers_license_type.label,
                    "key": self.drivers_license_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.drivers_license.document_number,
            },
            {
                "id": encode_id_base64_required(self.tax_id.id, "Document"),
                "type": {
                    "id": encode_id_base64_required(self.tax_id_type.id, "DocumentType"),
                    "label": self.tax_id_type.label,
                    "key": self.tax_id_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.tax_id.document_number,
            },
        ]

        assert data["identities"] == [
            {
                "id": encode_id_base64_required(self.identity.id, "IndividualIdentity"),
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "number": self.identity.number,
            }
        ]

        assert data["bank_account_info"] == [
            {
                "id": encode_id_base64_required(self.bank_account_info.id, "BankAccountInfo"),
                "bank_name": self.bank_account_info.bank_name,
                "bank_account_number": self.bank_account_info.bank_account_number,
                "account_holder_name": self.bank_account_info.account_holder_name,
                "bank_branch_name": self.bank_account_info.bank_branch_name,
            }
        ]

        assert data["delivery_mechanisms_data"] == [
            {
                "id": encode_id_base64_required(self.dm_atm_card_data.id, "DeliveryMechanismData"),
                "name": self.account_type_bank.label,
                "individual_tab_data": {
                    "card_number": "123",
                    "card_expiry_date": "2022-01-01",
                    "name_of_cardholder": "Marek",
                },
            },
            {
                "id": encode_id_base64_required(self.dm_mobile_money_data.id, "DeliveryMechanismData"),
                "name": self.account_type_mobile.label,
                "individual_tab_data": {
                    "service_provider_code": "ABC",
                    "delivery_phone_number": "123456789",
                    "provider": "Provider",
                },
            },
        ]

        assert data["linked_grievances"] == [
            {
                "id": encode_id_base64_required(self.grievance_ticket.id, "GrievanceTicket"),
                "category": self.grievance_ticket.category,
                "status": self.grievance_ticket.status,
            }
        ]


class TestIndividualGlobalViewSet:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.global_url_name = "api:households:individuals-global-list"
        self.global_count_url = "api:households:individuals-global-count"
        self.afghanistan = create_afghanistan()
        self.ukraine = create_ukraine()
        self.program_afghanistan1 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 1",
        )
        self.program_afghanistan2 = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.ACTIVE,
            name="program afghanistan 2",
        )
        self.program_ukraine = ProgramFactory(business_area=self.ukraine, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        self.admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=self.admin_type_1)
        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=self.admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)
        self.area3 = AreaFactory(parent=self.area2, p_code="AF010101", area_type=admin_type_2)
        self.area4 = AreaFactory(parent=self.area3, p_code="AF01010101", area_type=admin_type_2)

        self.household_afghanistan1, (
            self.individual_afghanistan1_1,
            self.individual_afghanistan1_2,
        ) = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        self.household_afghanistan2, (
            self.individual_afghanistan2_1,
            self.individual_afghanistan2_2,
        ) = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        self.household_ukraine, (
            self.individual_ukraine_1,
            self.individual_ukraine_2,
        ) = create_household_and_individuals(
            household_data={
                "admin_area": self.area1,
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "program": self.program_ukraine,
                "business_area": self.ukraine,
            },
            individuals_data=[{}, {}],
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.POPULATION_VIEW_INDIVIDUALS_LIST], status.HTTP_200_OK),
            ([Permissions.RDI_VIEW_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_individual_global_list_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == expected_status

    def test_individual_global_list(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 4

        response_count = self.api_client.get(
            reverse(self.global_count_url, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 4

        result_ids = [result["id"] for result in response_results]
        assert get_encoded_individual_id(self.individual_afghanistan1_1) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan1_2) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_1) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_2) in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_1) not in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_2) not in result_ids

        for i, individual in enumerate(
            [
                self.individual_afghanistan1_1,
                self.individual_afghanistan1_2,
                self.individual_afghanistan2_1,
                self.individual_afghanistan2_2,
            ]
        ):
            individual_result = response_results[i]
            assert individual_result["id"] == get_encoded_individual_id(individual)
            assert individual_result["unicef_id"] == individual.unicef_id
            assert individual_result["full_name"] == individual.full_name
            assert individual_result["status"] == individual.status
            assert individual_result["relationship"] == individual.relationship
            assert individual_result["age"] == individual.age
            assert individual_result["sex"] == individual.sex
            assert individual_result["household"] == {
                "id": get_encoded_household_id(individual.household),
                "unicef_id": individual.household.unicef_id,
                "admin2": individual.household.admin2.name,
            }

    def test_individual_global_list_with_permissions_in_one_program(
        self, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            program=self.program_afghanistan1,
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2

        result_ids = [result["id"] for result in response_results]
        assert get_encoded_individual_id(self.individual_afghanistan1_1) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan1_2) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_1) not in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_2) not in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_1) not in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_2) not in result_ids

    def test_individual_global_list_area_limits(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program_afghanistan2, [self.area1, self.area2])
        household_afghanistan_without_areas, (
            individual_afghanistan_without_areas1,
            individual_afghanistan_without_areas2,
        ) = create_household_and_individuals(
            household_data={
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.admin_type_1)
        household_afghanistan_different_areas, (
            individual_afghanistan_different_areas1,
            individual_afghanistan_different_areas2,
        ) = create_household_and_individuals(
            household_data={
                "admin_area": area_different,
                "admin1": area_different,
                "admin2": area_different,
                "admin3": area_different,
                "admin4": area_different,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        response = self.api_client.get(
            reverse(self.global_url_name, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 6

        result_ids = [result["id"] for result in response_results]
        assert get_encoded_individual_id(self.individual_afghanistan1_1) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan1_2) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_1) in result_ids
        assert get_encoded_individual_id(self.individual_afghanistan2_2) in result_ids
        assert get_encoded_individual_id(individual_afghanistan_without_areas1) in result_ids
        assert get_encoded_individual_id(individual_afghanistan_without_areas2) in result_ids
        assert get_encoded_individual_id(individual_afghanistan_different_areas1) not in result_ids
        assert get_encoded_individual_id(individual_afghanistan_different_areas2) not in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_1) not in result_ids
        assert get_encoded_individual_id(self.individual_ukraine_2) not in result_ids


class TestIndividualFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.list_url = reverse(
            "api:households:individuals-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

    def _create_test_individuals(
        self,
        individual1_data: Optional[dict] = None,
        individual2_data: Optional[dict] = None,
        household1_data: Optional[dict] = None,
        household2_data: Optional[dict] = None,
    ) -> Tuple[Individual, Individual]:
        if individual1_data is None:
            individual1_data = {}
        if individual2_data is None:
            individual2_data = {}
        if household1_data is None:
            household1_data = {}
        if household2_data is None:
            household2_data = {}
        _, (individual1,) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
                **household1_data,
            },
            individuals_data=[individual1_data],
        )
        _, (individual2,) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
                **household2_data,
            },
            individuals_data=[individual2_data],
        )
        return individual1, individual2

    def _test_filter_individuals_in_list(
        self,
        filters: dict,
        individual1_data: Optional[dict] = None,
        individual2_data: Optional[dict] = None,
        household1_data: Optional[dict] = None,
        household2_data: Optional[dict] = None,
    ) -> None:
        individual1, individual2 = self._create_test_individuals(
            individual1_data=individual1_data,
            individual2_data=individual2_data,
            household1_data=household1_data,
            household2_data=household2_data,
        )
        response = self.api_client.get(self.list_url, filters)
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == get_encoded_individual_id(individual2)
        return response_data

    def test_filter_by_rdi_id(self) -> None:
        registration_data_import_1 = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        registration_data_import_2 = RegistrationDataImportFactory(
            imported_by=self.user, business_area=self.afghanistan, program=self.program
        )
        self._test_filter_individuals_in_list(
            filters={"rdi_id": registration_data_import_2.id},
            individual1_data={
                "registration_data_import": registration_data_import_1,
            },
            individual2_data={
                "registration_data_import": registration_data_import_2,
            },
        )

    def test_filter_by_document_number(self) -> None:
        document_passport = DocumentTypeFactory(key="passport")
        document_id_card = DocumentTypeFactory(key="id_card")
        individual1, individual2 = self._create_test_individuals()
        individual3, individual4 = self._create_test_individuals()
        DocumentFactory(individual=individual1, type=document_passport, document_number="123")
        DocumentFactory(individual=individual2, type=document_passport, document_number="456")
        DocumentFactory(individual=individual3, type=document_id_card, document_number="123")
        DocumentFactory(individual=individual4, type=document_id_card, document_number="456")
        response = self.api_client.get(self.list_url, {"document_number": "456", "document_type": "passport"})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == get_encoded_individual_id(individual2)

    def test_filter_by_full_name(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"full_name": "John"},
            individual1_data={"full_name": "Jane Doe"},
            individual2_data={"full_name": "John Doe"},
        )

    def test_filter_by_sex(self) -> None:
        individual_m, individual_f = self._create_test_individuals(
            individual1_data={"sex": MALE},
            individual2_data={"sex": FEMALE},
        )
        individual_o, individual_nc = self._create_test_individuals(
            individual1_data={"sex": OTHER},
            individual2_data={"sex": NOT_COLLECTED},
        )
        response_male = self.api_client.get(self.list_url, {"sex": "MALE"})
        assert response_male.status_code == status.HTTP_200_OK
        response_data_male = response_male.json()["results"]
        assert len(response_data_male) == 1
        assert response_data_male[0]["id"] == get_encoded_individual_id(individual_m)

        response_male_female = self.api_client.get(self.list_url, {"sex": ["MALE", "FEMALE"]})
        assert response_male_female.status_code == status.HTTP_200_OK
        response_data_male_female = response_male_female.json()["results"]
        assert len(response_data_male_female) == 2
        individuals_ids = [individual["id"] for individual in response_data_male_female]
        assert get_encoded_individual_id(individual_m) in individuals_ids
        assert get_encoded_individual_id(individual_f) in individuals_ids
        assert get_encoded_individual_id(individual_o) not in individuals_ids
        assert get_encoded_individual_id(individual_nc) not in individuals_ids

    def test_filter_by_status(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"status": STATUS_ACTIVE},
            individual1_data={"duplicate": True},
            individual2_data={"duplicate": False, "withdrawn": False},
        )

    def test_filter_by_flags(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"flags": NEEDS_ADJUDICATION},
            individual1_data={},
            individual2_data={"deduplication_golden_record_status": NEEDS_ADJUDICATION},
        )

    def test_filter_by_withdrawn(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"withdrawn": True},
            individual1_data={"withdrawn": False},
            individual2_data={"withdrawn": True},
        )

    def test_filter_by_excluded_id(self) -> None:
        individual1, individual2 = self._create_test_individuals()
        response_excluded = self.api_client.get(self.list_url, {"excluded_id": get_encoded_individual_id(individual1)})
        assert response_excluded.status_code == status.HTTP_200_OK
        response_data_male = response_excluded.json()["results"]
        assert len(response_data_male) == 1
        assert response_data_male[0]["id"] == get_encoded_individual_id(individual2)

    @pytest.mark.parametrize(
        "program_status,filter_value,expected_results",
        [
            (Program.ACTIVE, True, 2),
            (Program.FINISHED, True, 0),
            (Program.ACTIVE, False, 0),
            (Program.FINISHED, False, 2),
        ],
    )
    def test_filter_by_is_active_program(self, program_status: str, filter_value: bool, expected_results: int) -> None:
        self.program.status = program_status
        self.program.save()

        self._create_test_individuals()
        response = self.api_client.get(self.list_url, {"is_active_program": filter_value})
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()["results"]
        assert len(response_data) == expected_results

    def test_filter_by_rdi_merge_status(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"rdi_merge_status": MergeStatusModel.PENDING},
            individual1_data={"rdi_merge_status": MergeStatusModel.MERGED},
            individual2_data={"rdi_merge_status": MergeStatusModel.PENDING},
        )

    @pytest.mark.parametrize(
        "filter_by_field",
        [
            "admin1",
            "admin2",
        ],
    )
    def test_filter_by_area(self, filter_by_field: str) -> None:
        country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=country, area_level=2, parent=admin_type_1)
        area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        area2 = AreaFactory(parent=area1, p_code="AF0101", area_type=admin_type_2)
        encoded_id = encode_id_base64_required(area2.id, "Area")
        self._test_filter_individuals_in_list(
            filters={filter_by_field: encoded_id},
            household1_data={filter_by_field: area1},
            household2_data={filter_by_field: area2},
        )

    def test_filter_by_last_registration_date(self) -> None:
        individual1, individual2 = self._create_test_individuals(
            individual1_data={"last_registration_date": timezone.make_aware(timezone.datetime(2021, 1, 1))},
            individual2_data={"last_registration_date": timezone.make_aware(timezone.datetime(2023, 1, 1))},
        )
        response_after = self.api_client.get(self.list_url, {"last_registration_date_after": "2022-12-31"})
        assert response_after.status_code == status.HTTP_200_OK
        response_data_after = response_after.json()["results"]
        assert len(response_data_after) == 1
        assert response_data_after[0]["id"] == get_encoded_individual_id(individual2)

        response_before = self.api_client.get(self.list_url, {"last_registration_date_before": "2022-12-31"})
        assert response_before.status_code == status.HTTP_200_OK
        response_data_before = response_after.json()["results"]
        assert len(response_data_before) == 1
        assert response_data_before[0]["id"] == get_encoded_individual_id(individual2)
        return response_data_before

    def test_filter_by_duplicates_only(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"duplicates_only": True},
            individual1_data={"deduplication_golden_record_status": UNIQUE},
            individual2_data={"deduplication_golden_record_status": DUPLICATE},
        )

    @override_config(USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH=True)
    @pytest.mark.parametrize(
        "filters,individual1_data,individual2_data,household1_data,household2_data",
        [
            ({"search": "IND-123"}, {"unicef_id": "IND-321"}, {"unicef_id": "IND-123"}, {}, {}),
            ({"search": "HH-123"}, {}, {}, {"unicef_id": "HH-321"}, {"unicef_id": "HH-123"}),
            ({"search": "John Root"}, {"full_name": "Jack Root"}, {"full_name": "John Root"}, {}, {}),
            ({"search": "+48010101010"}, {"phone_no": "+48 609 456 008"}, {"phone_no": "+48 010 101 010"}, {}, {}),
            ({"search": "HOPE-123"}, {"detail_id": "HOPE-321"}, {"detail_id": "HOPE-123"}, {}, {}),
            ({"search": "456"}, {"program_registration_id": "123"}, {"program_registration_id": "456"}, {}, {}),
        ],
    )
    def test_search(
        self,
        filters: Dict,
        individual1_data: Dict,
        individual2_data: Dict,
        household1_data: Dict,
        household2_data: Dict,
    ) -> None:
        individual1, individual2 = self._create_test_individuals(
            individual1_data=individual1_data,
            individual2_data=individual2_data,
            household1_data=household1_data,
            household2_data=household2_data,
        )
        rebuild_search_index()
        response = self.api_client.get(self.list_url, filters)
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]

        assert len(response_data) == 1
        assert response_data[0]["id"] == get_encoded_individual_id(individual2)
        return response_data

    @override_config(USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH=True)
    def test_search_by_bank_account_number(self) -> None:
        _, (individual1, _) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        _, (individual2, _) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        BankAccountInfoFactory(bank_account_number="123456789", individual=individual1)
        BankAccountInfoFactory(bank_account_number="987654321", individual=individual2)
        rebuild_search_index()
        response = self.api_client.get(self.list_url, {"search": "987654321"})
        assert response.status_code == status.HTTP_200_OK, response.json()
        response_data = response.json()["results"]
        assert len(response_data) == 1
        assert response_data[0]["id"] == get_encoded_individual_id(individual2)
        return response_data

    def test_filter_by_age(self) -> None:
        individual_age_5, individual_age_10 = self._create_test_individuals(
            individual1_data={"birth_date": "2014-10-10"},
            individual2_data={"birth_date": "2009-10-10"},
        )
        individual_age_15, individual_age_20 = self._create_test_individuals(
            individual1_data={"birth_date": "2004-10-10"},
            individual2_data={"birth_date": "1999-10-10"},
        )
        with freezegun.freeze_time("2019-11-10"):
            response_min = self.api_client.get(self.list_url, {"age_min": 8})
            assert response_min.status_code == status.HTTP_200_OK
            response_data_min = response_min.json()["results"]
            assert len(response_data_min) == 3
            individuals_ids_min = [individual["id"] for individual in response_data_min]
            assert get_encoded_individual_id(individual_age_10) in individuals_ids_min
            assert get_encoded_individual_id(individual_age_15) in individuals_ids_min
            assert get_encoded_individual_id(individual_age_20) in individuals_ids_min
            assert get_encoded_individual_id(individual_age_5) not in individuals_ids_min

            response_max = self.api_client.get(self.list_url, {"age_max": 12})
            assert response_max.status_code == status.HTTP_200_OK
            response_data_max = response_max.json()["results"]
            assert len(response_data_max) == 2
            individuals_ids_max = [individual["id"] for individual in response_data_max]
            assert get_encoded_individual_id(individual_age_5) in individuals_ids_max
            assert get_encoded_individual_id(individual_age_10) in individuals_ids_max
            assert get_encoded_individual_id(individual_age_15) not in individuals_ids_max
            assert get_encoded_individual_id(individual_age_20) not in individuals_ids_max

            response_min_max = self.api_client.get(
                self.list_url,
                {"age_min": 8, "age_max": 12},
            )
            assert response_min_max.status_code == status.HTTP_200_OK
            response_data_min_max = response_min_max.json()["results"]
            assert len(response_data_min_max) == 1
            individuals_ids_min_max = [individual["id"] for individual in response_data_min_max]
            assert get_encoded_individual_id(individual_age_10) in individuals_ids_min_max
            assert get_encoded_individual_id(individual_age_5) not in individuals_ids_min_max
            assert get_encoded_individual_id(individual_age_15) not in individuals_ids_min_max
            assert get_encoded_individual_id(individual_age_20) not in individuals_ids_min_max
