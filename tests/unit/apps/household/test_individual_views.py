import json
from typing import Any, Dict, List, Optional, Tuple

import freezegun
import pytest
from constance.test import override_config
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import (
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    create_ukraine,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import (
    DocumentFactory,
    DocumentTypeFactory,
    IndividualIdentityFactory,
    IndividualRoleInHouseholdFactory,
    create_household_and_individuals,
)
from extras.test_utils.factories.payment import (
    AccountFactory,
    generate_delivery_mechanisms,
)
from extras.test_utils.factories.program import ProgramFactory
from extras.test_utils.factories.registration_data import RegistrationDataImportFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.models.core import FlexibleAttribute, PeriodicFieldData
from hope.apps.core.utils import to_choice_object
from hope.models.household import (
    AGENCY_TYPE_CHOICES,
    CANNOT_DO,
    DEDUPLICATION_BATCH_STATUS_CHOICE,
    DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE,
    DISABLED,
    DUPLICATE,
    FEMALE,
    HEARING,
    INDIVIDUAL_FLAGS_CHOICES,
    INDIVIDUAL_STATUS_CHOICES,
    LOT_DIFFICULTY,
    MALE,
    MARITAL_STATUS_CHOICE,
    NEEDS_ADJUDICATION,
    NOT_COLLECTED,
    OBSERVED_DISABILITY_CHOICE,
    OTHER,
    RELATIONSHIP_CHOICE,
    ROLE_ALTERNATE,
    ROLE_CHOICE,
    ROLE_PRIMARY,
    SEEING,
    SEVERITY_OF_DISABILITY_CHOICES,
    SEX_CHOICE,
    STATUS_ACTIVE,
    UNIQUE,
    WORK_STATUS_CHOICE,
    DocumentType,
    Household,
    Individual,
)
from hope.apps.payment.models import AccountType, FinancialInstitution
from hope.apps.periodic_data_update.utils import populate_pdu_with_null_values
from hope.models.program import Program
from hope.apps.utils.elasticsearch_utils import rebuild_search_index
from hope.models.utils import MergeStatusModel

pytestmark = pytest.mark.django_db()


class TestIndividualList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        different_program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:households:individuals-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
            },
        )
        self.count_url = reverse(
            "api:households:individuals-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
            },
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.country = CountryFactory()
        admin_type_1 = AreaTypeFactory(country=self.country, area_level=1)
        admin_type_2 = AreaTypeFactory(country=self.country, area_level=2, parent=admin_type_1)

        self.area1 = AreaFactory(parent=None, p_code="AF01", area_type=admin_type_1)
        self.area2 = AreaFactory(parent=self.area1, p_code="AF0101", area_type=admin_type_2)

        (
            self.household1,
            (
                self.individual1_1,
                self.individual1_2,
            ),
        ) = self._create_household(self.program)
        (
            self.household2,
            (
                self.individual2_1,
                self.individual2_2,
            ),
        ) = self._create_household(self.program)
        (
            self.household_from_different_program,
            (
                self.individual_from_different_program_1,
                self.individual_from_different_program_2,
            ),
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
        ("permissions", "expected_status"),
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
        ("permissions", "expected_status"),
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
        assert str(self.individual1_1.id) in response_ids
        assert str(self.individual1_2.id) in response_ids
        assert str(self.individual2_1.id) in response_ids
        assert str(self.individual2_2.id) in response_ids

        for i, individual in enumerate(
            [
                self.individual1_1,
                self.individual1_2,
                self.individual2_1,
                self.individual2_2,
            ]
        ):
            individual_result = response_results[i]
            assert individual_result["id"] == str(individual.id)
            assert individual_result["unicef_id"] == individual.unicef_id
            assert individual_result["full_name"] == individual.full_name
            assert individual_result["status"] == individual.status
            assert individual_result["relationship"] == individual.relationship
            assert individual_result["age"] == individual.age
            assert individual_result["sex"] == individual.sex
            assert individual_result["household"] == {
                "id": str(individual.household.id),
                "unicef_id": individual.household.unicef_id,
                "admin1": {
                    "id": str(individual.household.admin1.id),
                    "name": individual.household.admin1.name,
                },
                "admin2": {
                    "id": str(individual.household.admin2.id),
                    "name": individual.household.admin2.name,
                },
                "admin3": None,
                "admin4": None,
                "first_registration_date": f"{individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": individual.household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": individual.household.get_residence_status_display(),
                "country_origin": individual.household.country_origin.name,
                "country": individual.household.country.name,
                "address": individual.household.address,
                "village": individual.household.village,
                "geopoint": None,
                "import_id": individual.household.unicef_id,
                "program_slug": individual.program.slug,
            }
            assert individual_result["program"] == {
                "id": str(individual.program.id),
                "name": individual.program.name,
                "slug": individual.program.slug,
                "programme_code": individual.program.programme_code,
                "status": individual.program.status,
                "screen_beneficiary": individual.program.screen_beneficiary,
            }
            assert individual_result["last_registration_date"] == f"{individual.last_registration_date:%Y-%m-%d}"

    def test_individual_list_on_draft_program(self, create_user_role_with_permissions: Any) -> None:
        program = ProgramFactory(business_area=self.afghanistan, status=Program.DRAFT)
        list_url = reverse(
            "api:households:individuals-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": program.slug,
            },
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
        self,
        create_user_role_with_permissions: Any,
        set_admin_area_limits_in_program: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.RDI_VIEW_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])

        (
            household_without_areas,
            (
                individual_without_areas1,
                individual_without_areas2,
            ),
        ) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.area1.area_type)
        (
            household_different_areas,
            (
                individual_different_areas1,
                individual_different_areas2,
            ),
        ) = self._create_household(self.program)
        household_different_areas.admin1 = area_different
        household_different_areas.admin2 = area_different
        household_different_areas.save()

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 6

        response_ids = [result["id"] for result in response_results]
        assert str(self.individual1_1.id) in response_ids
        assert str(self.individual1_2.id) in response_ids
        assert str(self.individual2_1.id) in response_ids
        assert str(self.individual2_2.id) in response_ids
        assert str(individual_without_areas1.id) in response_ids
        assert str(individual_without_areas2.id) in response_ids
        assert str(individual_different_areas1.id) not in response_ids
        assert str(individual_different_areas2.id) not in response_ids

    def test_individual_list_caching(
        self,
        create_user_role_with_permissions: Any,
        set_admin_area_limits_in_program: Any,
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
            assert len(ctx.captured_queries) == 36

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
            assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            assert len(ctx.captured_queries) == 31

        set_admin_area_limits_in_program(self.partner, self.program, [self.area1])
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_changed_areas = response.headers["etag"]
            assert json.loads(cache.get(etag_changed_areas)[0].decode("utf8")) == response.json()
            assert etag_changed_areas not in [etag, etag_second_call, etag_third_call]
            assert len(ctx.captured_queries) == 31

        self.individual1_1.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert len(response.json()["results"]) == 3
            assert etag_fourth_call not in [
                etag,
                etag_second_call,
                etag_third_call,
                etag_changed_areas,
            ]
            assert len(ctx.captured_queries) == 27

        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 10

    def test_individual_list_deduplication_result_serializer(self, create_user_role_with_permissions: Any) -> None:
        _, (duplicate_individual,) = create_household_and_individuals(
            household_data={
                "program": self.program,
                "business_area": self.afghanistan,
            },
            individuals_data=[{"full_name": "das asd asd", "birth_date": "1981-03-11"}],
        )
        self.individual1_1.deduplication_golden_record_status = DUPLICATE
        self.individual1_1.deduplication_golden_record_results = {
            "duplicates": [
                {
                    "dob": "1981-03-11",
                    "score": 25.0,
                    "hit_id": str(duplicate_individual.id),
                    "location": None,
                    "full_name": duplicate_individual.full_name,
                    "proximity_to_score": 14.0,
                }
            ],
            "possible_duplicates": [],
        }
        self.individual1_1.save()

        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        ind = next(r for r in results if r["id"] == str(self.individual1_1.id))
        assert "deduplication_golden_record_results" in ind
        assert ind["deduplication_golden_record_results"][0]["hit_id"] == str(duplicate_individual.id)
        assert ind["deduplication_golden_record_results"][0]["full_name"] == "das asd asd"
        assert ind["deduplication_golden_record_results"][0]["age"] == 44
        assert ind["deduplication_golden_record_results"][0]["score"] == 25.0
        assert ind["deduplication_golden_record_results"][0]["proximity_to_score"] == 14.0
        assert ind["deduplication_golden_record_results"][0]["location"] is None

    def test_individual_all_flex_fields_attributes(self, create_user_role_with_permissions: Any) -> None:
        program = ProgramFactory(business_area=self.afghanistan, status=Program.DRAFT)
        list_url = reverse(
            "api:households:individuals-all-flex-fields-attributes",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": program.slug,
            },
        )
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS],
            business_area=self.afghanistan,
            program=program,
        )
        FlexibleAttribute.objects.create(
            name="Flexible Attribute for INDIVIDUAL",
            type=FlexibleAttribute.STRING,
            label={"English(EN)": "Test Flex", "Test": ""},
            associated_with=FlexibleAttribute.ASSOCIATED_WITH_INDIVIDUAL,
            program=program,
        )

        response = self.api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Flexible Attribute for INDIVIDUAL"


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
        (
            self.household,
            (
                self.individual1,
                self.individual2,
            ),
        ) = create_household_and_individuals(
            household_data={
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
                    "photo": ContentFile(b"abc", name="1.png"),
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

        self.grievance_ticket = GrievanceTicketFactory(household_unicef_id=self.household.unicef_id)
        GrievanceTicketFactory()

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
            photo=ContentFile(b"abc", name="doc.png"),
        )

        self.national_passport = DocumentFactory(
            document_number="111-222-333",
            type=DocumentTypeFactory(key="national_passport"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
            photo=ContentFile(b"abc", name="doc2.png"),
        )

        self.birth_certificate = DocumentFactory(
            document_number="111222333",
            type=DocumentType.objects.get(key="birth_certificate"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
            photo=ContentFile(b"abc", name="doc3.png"),
        )

        self.disability_card = DocumentFactory(
            document_number="10000000000",
            type=DocumentType.objects.get(key="disability_card"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
            photo=ContentFile(b"abc", name="doc4.png"),
        )

        self.drivers_license = DocumentFactory(
            document_number="1234567890",
            type=DocumentType.objects.get(key="drivers_license"),
            individual=self.individual1,
            program=self.program,
            photo=ContentFile(b"abc", name="doc5.png"),
        )

        self.tax_id = DocumentFactory(
            document_number="666-777-888",
            type=DocumentType.objects.get(key="tax_id"),
            individual=self.individual1,
            program=self.program,
            country=self.country,
            photo=ContentFile(b"abc", name="doc6.png"),
        )

        self.identity = IndividualIdentityFactory(
            country=self.country,
            individual=self.individual1,
        )

        generate_delivery_mechanisms()
        AccountFactory(
            individual=self.individual1,
            data={
                "card_number__bank": "123",
                "card_expiry_date__bank": "2022-01-01",
                "name_of_cardholder__bank": "Marek",
            },
        )
        AccountFactory(
            individual=self.individual1,
            data={
                "service_provider_code__mobile": "ABC",
                "delivery_phone_number__mobile": "123456789",
                "provider__mobile": "Provider",
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
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
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": str(self.individual1.id),
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
        response = self.api_client.get(
            reverse(
                self.detail_url_name,
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": str(self.individual1.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.data

        assert data["id"] == str(self.individual1.id)
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
            "id": str(self.individual1.household.id),
            "unicef_id": self.individual1.household.unicef_id,
            "admin1": {
                "id": str(self.individual1.household.admin1.id),
                "name": self.individual1.household.admin1.name,
            },
            "admin2": {
                "id": str(self.individual1.household.admin2.id),
                "name": self.individual1.household.admin2.name,
            },
            "admin3": {
                "id": str(self.individual1.household.admin3.id),
                "name": self.individual1.household.admin3.name,
            },
            "admin4": {
                "id": str(self.individual1.household.admin4.id),
                "name": self.individual1.household.admin4.name,
            },
            "first_registration_date": f"{self.individual1.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
            "last_registration_date": f"{self.individual1.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
            "total_cash_received": None,
            "total_cash_received_usd": None,
            "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
            "start": self.individual1.household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "zip_code": None,
            "residence_status": self.individual1.household.get_residence_status_display(),
            "country_origin": self.individual1.household.country_origin.name,
            "country": self.individual1.household.country.name,
            "address": self.individual1.household.address,
            "village": self.individual1.household.village,
            "geopoint": None,
            "import_id": self.individual1.household.unicef_id,
            "program_slug": self.program.slug,
        }
        assert data["role"] == ROLE_PRIMARY
        assert data["relationship"] == self.individual1.relationship
        assert data["registration_data_import"] == {
            "id": str(self.registration_data_import.id),
            "name": self.registration_data_import.name,
            "status": self.registration_data_import.status,
            "import_date": f"{self.registration_data_import.import_date:%Y-%m-%dT%H:%M:%S.%fZ}",
            "number_of_individuals": self.registration_data_import.number_of_individuals,
            "number_of_households": self.registration_data_import.number_of_households,
            "imported_by": {
                "id": str(self.registration_data_import.imported_by.id),
                "first_name": self.registration_data_import.imported_by.first_name,
                "last_name": self.registration_data_import.imported_by.last_name,
                "email": self.registration_data_import.imported_by.email,
                "username": self.registration_data_import.imported_by.username,
            },
            "data_source": self.registration_data_import.data_source,
        }
        assert data["import_id"] == self.individual1.unicef_id
        assert data["admin_url"] == self.individual1.admin_url
        assert data["preferred_language"] == self.individual1.preferred_language
        assert data["roles_in_households"] == [
            {
                "id": str(self.role_primary.id),
                "household": {
                    "id": str(self.household.id),
                    "unicef_id": self.household.unicef_id,
                    "admin1": {
                        "id": str(self.household.admin1.id),
                        "name": self.household.admin1.name,
                    },
                    "admin2": {
                        "id": str(self.household.admin2.id),
                        "name": self.household.admin2.name,
                    },
                    "admin3": {
                        "id": str(self.household.admin3.id),
                        "name": self.household.admin3.name,
                    },
                    "admin4": {
                        "id": str(self.household.admin4.id),
                        "name": self.household.admin4.name,
                    },
                    "first_registration_date": f"{self.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "last_registration_date": f"{self.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "total_cash_received": None,
                    "total_cash_received_usd": None,
                    "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                    "start": self.household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "zip_code": None,
                    "residence_status": self.household.get_residence_status_display(),
                    "country_origin": self.household.country_origin.name,
                    "country": self.household.country.name,
                    "address": self.household.address,
                    "village": self.household.village,
                    "geopoint": None,
                    "import_id": self.household.unicef_id,
                    "program_slug": self.program.slug,
                },
                "role": ROLE_PRIMARY,
            },
            {
                "id": str(self.role_alternate.id),
                "household": {
                    "id": str(self.household2.id),
                    "unicef_id": self.household2.unicef_id,
                    "admin1": None,
                    "admin2": None,
                    "admin3": None,
                    "admin4": None,
                    "first_registration_date": f"{self.household2.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "last_registration_date": f"{self.household2.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                    "total_cash_received": None,
                    "total_cash_received_usd": None,
                    "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                    "start": self.household2.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "zip_code": None,
                    "residence_status": self.household2.get_residence_status_display(),
                    "country_origin": self.household2.country_origin.name,
                    "country": self.household2.country.name,
                    "address": self.household2.address,
                    "village": self.household2.village,
                    "geopoint": None,
                    "import_id": self.household2.unicef_id,
                    "program_slug": self.program.slug,
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
                "id": str(self.national_id.id),
                "type": {
                    "id": str(self.national_id_type.id),
                    "label": self.national_id_type.label,
                    "key": self.national_id_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.national_id.document_number,
                "photo": self.national_id.photo.url,
            },
            {
                "id": str(self.national_passport.id),
                "type": {
                    "id": str(self.national_passport_type.id),
                    "label": self.national_passport_type.label,
                    "key": self.national_passport_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.national_passport.document_number,
                "photo": self.national_passport.photo.url,
            },
            {
                "id": str(self.birth_certificate.id),
                "type": {
                    "id": str(self.birth_certificate_type.id),
                    "label": self.birth_certificate_type.label,
                    "key": self.birth_certificate_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.birth_certificate.document_number,
                "photo": self.birth_certificate.photo.url,
            },
            {
                "id": str(self.disability_card.id),
                "type": {
                    "id": str(self.disability_card_type.id),
                    "label": self.disability_card_type.label,
                    "key": self.disability_card_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.disability_card.document_number,
                "photo": self.disability_card.photo.url,
            },
            {
                "id": str(self.drivers_license.id),
                "type": {
                    "id": str(self.drivers_license_type.id),
                    "label": self.drivers_license_type.label,
                    "key": self.drivers_license_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.drivers_license.document_number,
                "photo": self.drivers_license.photo.url,
            },
            {
                "id": str(self.tax_id.id),
                "type": {
                    "id": str(self.tax_id_type.id),
                    "label": self.tax_id_type.label,
                    "key": self.tax_id_type.key,
                },
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "document_number": self.tax_id.document_number,
                "photo": self.tax_id.photo.url,
            },
        ]
        assert data["identities"] == [
            {
                "id": self.identity.id,
                "country": {
                    "id": str(self.country.id),
                    "name": self.country.name,
                    "iso_code3": self.country.iso_code3,
                },
                "partner": None,
                "number": self.identity.number,
            }
        ]
        assert len(data["accounts"]) == 2
        account_1 = data["accounts"][0]
        account_2 = data["accounts"][1]
        assert account_1["data_fields"] == {
            "card_expiry_date__bank": "2022-01-01",
            "card_number__bank": "123",
            "name_of_cardholder__bank": "Marek",
        }
        assert account_2["data_fields"] == {
            "service_provider_code__mobile": "ABC",
            "delivery_phone_number__mobile": "123456789",
            "provider__mobile": "Provider",
        }

        assert data["linked_grievances"] == [
            {
                "id": str(self.grievance_ticket.id),
                "category": self.grievance_ticket.category,
                "status": self.grievance_ticket.status,
            }
        ]
        assert data["enrolled_in_nutrition_programme"] == self.individual1.enrolled_in_nutrition_programme
        assert data["who_answers_phone"] == self.individual1.who_answers_phone
        assert data["who_answers_alt_phone"] == self.individual1.who_answers_alt_phone
        assert data["payment_delivery_phone_no"] == self.individual1.payment_delivery_phone_no

    def test_get_individual_photos(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[
                Permissions.POPULATION_VIEW_INDIVIDUALS_DETAILS,
            ],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(
            reverse(
                "api:households:individuals-photos",
                kwargs={
                    "business_area_slug": self.afghanistan.slug,
                    "program_slug": self.program.slug,
                    "pk": str(self.individual1.id),
                },
            )
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert data["id"] == str(self.individual1.id)
        assert data["photo"] is not None
        assert data["documents"][0]["document_number"] == "123-456-789"
        assert data["documents"][0]["photo"] is not None


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

        (
            self.household_afghanistan1,
            (
                self.individual_afghanistan1_1,
                self.individual_afghanistan1_2,
            ),
        ) = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "program": self.program_afghanistan1,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        (
            self.household_afghanistan2,
            (
                self.individual_afghanistan2_1,
                self.individual_afghanistan2_2,
            ),
        ) = create_household_and_individuals(
            household_data={
                "admin1": self.area1,
                "admin2": self.area2,
                "admin3": self.area3,
                "admin4": self.area4,
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )

        (
            self.household_ukraine,
            (
                self.individual_ukraine_1,
                self.individual_ukraine_2,
            ),
        ) = create_household_and_individuals(
            household_data={
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
        ("permissions", "expected_status"),
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
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
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
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 4

        response_count = self.api_client.get(
            reverse(
                self.global_count_url,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 4

        result_ids = [result["id"] for result in response_results]
        assert str(self.individual_afghanistan1_1.id) in result_ids
        assert str(self.individual_afghanistan1_2.id) in result_ids
        assert str(self.individual_afghanistan2_1.id) in result_ids
        assert str(self.individual_afghanistan2_2.id) in result_ids
        assert str(self.individual_ukraine_1.id) not in result_ids
        assert str(self.individual_ukraine_2.id) not in result_ids

        for i, individual in enumerate(
            [
                self.individual_afghanistan1_1,
                self.individual_afghanistan1_2,
                self.individual_afghanistan2_1,
                self.individual_afghanistan2_2,
            ]
        ):
            individual_result = response_results[i]
            assert individual_result["id"] == str(individual.id)
            assert individual_result["unicef_id"] == individual.unicef_id
            assert individual_result["full_name"] == individual.full_name
            assert individual_result["status"] == individual.status
            assert individual_result["relationship"] == individual.relationship
            assert individual_result["age"] == individual.age
            assert individual_result["sex"] == individual.sex
            assert individual_result["household"] == {
                "id": str(individual.household.id),
                "unicef_id": individual.household.unicef_id,
                "admin1": {
                    "id": str(individual.household.admin1.id),
                    "name": individual.household.admin1.name,
                },
                "admin2": {
                    "id": str(individual.household.admin2.id),
                    "name": individual.household.admin2.name,
                },
                "admin3": {
                    "id": str(individual.household.admin3.id),
                    "name": individual.household.admin3.name,
                },
                "admin4": {
                    "id": str(individual.household.admin4.id),
                    "name": individual.household.admin4.name,
                },
                "first_registration_date": f"{individual.household.first_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "last_registration_date": f"{individual.household.last_registration_date:%Y-%m-%dT%H:%M:%SZ}",
                "total_cash_received": None,
                "total_cash_received_usd": None,
                "delivered_quantities": [{"currency": "USD", "total_delivered_quantity": "0.00"}],
                "start": individual.household.start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "zip_code": None,
                "residence_status": individual.household.get_residence_status_display(),
                "country_origin": individual.household.country_origin.name,
                "country": individual.household.country.name,
                "address": individual.household.address,
                "village": individual.household.village,
                "geopoint": None,
                "import_id": individual.household.unicef_id,
                "program_slug": individual.program.slug,
            }
            assert individual_result["program"] == {
                "id": str(individual.program.id),
                "name": individual.program.name,
                "slug": individual.program.slug,
                "programme_code": individual.program.programme_code,
                "status": individual.program.status,
                "screen_beneficiary": individual.program.screen_beneficiary,
            }
            assert individual_result["last_registration_date"] == f"{individual.last_registration_date:%Y-%m-%d}"

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
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2

        result_ids = [result["id"] for result in response_results]
        assert str(self.individual_afghanistan1_1.id) in result_ids
        assert str(self.individual_afghanistan1_2.id) in result_ids
        assert str(self.individual_afghanistan2_1.id) not in result_ids
        assert str(self.individual_afghanistan2_2.id) not in result_ids
        assert str(self.individual_ukraine_1.id) not in result_ids
        assert str(self.individual_ukraine_2.id) not in result_ids

    def test_individual_global_list_area_limits(
        self,
        create_user_role_with_permissions: Any,
        set_admin_area_limits_in_program: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        set_admin_area_limits_in_program(self.partner, self.program_afghanistan2, [self.area1, self.area2])
        (
            household_afghanistan_without_areas,
            (
                individual_afghanistan_without_areas1,
                individual_afghanistan_without_areas2,
            ),
        ) = create_household_and_individuals(
            household_data={
                "program": self.program_afghanistan2,
                "business_area": self.afghanistan,
            },
            individuals_data=[{}, {}],
        )
        area_different = AreaFactory(parent=None, p_code="AF05", area_type=self.admin_type_1)
        (
            household_afghanistan_different_areas,
            (
                individual_afghanistan_different_areas1,
                individual_afghanistan_different_areas2,
            ),
        ) = create_household_and_individuals(
            household_data={
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
            reverse(
                self.global_url_name,
                kwargs={"business_area_slug": self.afghanistan.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 6

        result_ids = [result["id"] for result in response_results]
        assert str(self.individual_afghanistan1_1.id) in result_ids
        assert str(self.individual_afghanistan1_2.id) in result_ids
        assert str(self.individual_afghanistan2_1.id) in result_ids
        assert str(self.individual_afghanistan2_2.id) in result_ids
        assert str(individual_afghanistan_without_areas1.id) in result_ids
        assert str(individual_afghanistan_without_areas2.id) in result_ids
        assert str(individual_afghanistan_different_areas1.id) not in result_ids
        assert str(individual_afghanistan_different_areas2.id) not in result_ids
        assert str(self.individual_ukraine_1.id) not in result_ids
        assert str(self.individual_ukraine_2.id) not in result_ids


class TestIndividualChoices:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.choices_url = "api:households:individuals-global-choices"
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        DocumentTypeFactory(key="passport", label="Passport")
        DocumentTypeFactory(key="id_card", label="ID Card")
        DocumentTypeFactory(key="birth_certificate", label="Birth Certificate")

    def test_get_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.POPULATION_VIEW_INDIVIDUALS_LIST],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.choices_url, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "document_type_choices": [
                {"name": str(document_type.label), "value": document_type.key}
                for document_type in DocumentType.objects.order_by("key")
            ],
            "sex_choices": to_choice_object(SEX_CHOICE),
            "flag_choices": to_choice_object(INDIVIDUAL_FLAGS_CHOICES),
            "status_choices": to_choice_object(INDIVIDUAL_STATUS_CHOICES),
            "deduplication_batch_status_choices": to_choice_object(DEDUPLICATION_BATCH_STATUS_CHOICE),
            "deduplication_golden_record_status_choices": to_choice_object(DEDUPLICATION_GOLDEN_RECORD_STATUS_CHOICE),
            "relationship_choices": to_choice_object(RELATIONSHIP_CHOICE),
            "role_choices": to_choice_object(ROLE_CHOICE),
            "marital_status_choices": to_choice_object(MARITAL_STATUS_CHOICE),
            "identity_type_choices": to_choice_object(AGENCY_TYPE_CHOICES),
            "observed_disability_choices": to_choice_object(OBSERVED_DISABILITY_CHOICE),
            "severity_of_disability_choices": to_choice_object(SEVERITY_OF_DISABILITY_CHOICES),
            "work_status_choices": to_choice_object(WORK_STATUS_CHOICE),
            "account_type_choices": [{"name": x.label, "value": x.key} for x in AccountType.objects.all()],
            "account_financial_institution_choices": [
                {"name": x.name, "value": x.id} for x in FinancialInstitution.objects.all()
            ],
        }


class TestIndividualFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.list_url = reverse(
            "api:households:individuals-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
            },
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
        assert response_data[0]["id"] == str(individual2.id)
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
        assert response_data[0]["id"] == str(individual2.id)

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
        assert response_data_male[0]["id"] == str(individual_m.id)

        response_male_female = self.api_client.get(self.list_url, {"sex": ["MALE", "FEMALE"]})
        assert response_male_female.status_code == status.HTTP_200_OK
        response_data_male_female = response_male_female.json()["results"]
        assert len(response_data_male_female) == 2
        individuals_ids = [individual["id"] for individual in response_data_male_female]
        assert str(individual_m.id) in individuals_ids
        assert str(individual_f.id) in individuals_ids
        assert str(individual_o.id) not in individuals_ids
        assert str(individual_nc.id) not in individuals_ids

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
        response_excluded = self.api_client.get(self.list_url, {"excluded_id": str(individual1.id)})
        assert response_excluded.status_code == status.HTTP_200_OK
        response_data_male = response_excluded.json()["results"]
        assert len(response_data_male) == 1
        assert response_data_male[0]["id"] == str(individual2.id)

    @pytest.mark.parametrize(
        ("program_status", "filter_value", "expected_results"),
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
        self._test_filter_individuals_in_list(
            filters={filter_by_field: str(area2.id)},
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
        assert response_data_after[0]["id"] == str(individual2.id)

        response_before = self.api_client.get(self.list_url, {"last_registration_date_before": "2022-12-31"})
        assert response_before.status_code == status.HTTP_200_OK
        response_data_before = response_after.json()["results"]
        assert len(response_data_before) == 1
        assert response_data_before[0]["id"] == str(individual2.id)
        return response_data_before

    def test_filter_by_duplicates_only(self) -> None:
        self._test_filter_individuals_in_list(
            filters={"duplicates_only": True},
            individual1_data={"deduplication_golden_record_status": UNIQUE},
            individual2_data={"deduplication_golden_record_status": DUPLICATE},
        )

    @override_config(USE_ELASTICSEARCH_FOR_INDIVIDUALS_SEARCH=True)
    @pytest.mark.parametrize(
        (
            "filters",
            "individual1_data",
            "individual2_data",
            "household1_data",
            "household2_data",
        ),
        [
            (
                {"search": "IND-123"},
                {"unicef_id": "IND-321"},
                {"unicef_id": "IND-123"},
                {},
                {},
            ),
            (
                {"search": "HH-123"},
                {},
                {},
                {"unicef_id": "HH-321"},
                {"unicef_id": "HH-123"},
            ),
            (
                {"search": "John Root"},
                {"full_name": "Jack Root"},
                {"full_name": "John Root"},
                {},
                {},
            ),
            (
                {"search": "+48010101010"},
                {"phone_no": "+48 609 456 008"},
                {"phone_no": "+48 010 101 010"},
                {},
                {},
            ),
            (
                {"search": "HOPE-123"},
                {"detail_id": "HOPE-321"},
                {"detail_id": "HOPE-123"},
                {},
                {},
            ),
            (
                {"search": "456"},
                {"program_registration_id": "123"},
                {"program_registration_id": "456"},
                {},
                {},
            ),
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
        assert response_data[0]["id"] == str(individual2.id)

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
            assert str(individual_age_10.id) in individuals_ids_min
            assert str(individual_age_15.id) in individuals_ids_min
            assert str(individual_age_20.id) in individuals_ids_min
            assert str(individual_age_5.id) not in individuals_ids_min

            response_max = self.api_client.get(self.list_url, {"age_max": 12})
            assert response_max.status_code == status.HTTP_200_OK
            response_data_max = response_max.json()["results"]
            assert len(response_data_max) == 2
            individuals_ids_max = [individual["id"] for individual in response_data_max]
            assert str(individual_age_5.id) in individuals_ids_max
            assert str(individual_age_10.id) in individuals_ids_max
            assert str(individual_age_15.id) not in individuals_ids_max
            assert str(individual_age_20.id) not in individuals_ids_max

            response_min_max = self.api_client.get(
                self.list_url,
                {"age_min": 8, "age_max": 12},
            )
            assert response_min_max.status_code == status.HTTP_200_OK
            response_data_min_max = response_min_max.json()["results"]
            assert len(response_data_min_max) == 1
            individuals_ids_min_max = [individual["id"] for individual in response_data_min_max]
            assert str(individual_age_10.id) in individuals_ids_min_max
            assert str(individual_age_5.id) not in individuals_ids_min_max
            assert str(individual_age_15.id) not in individuals_ids_min_max
            assert str(individual_age_20.id) not in individuals_ids_min_max
