import datetime
from typing import Any, Callable

import pytest
from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.factories.core import (
    DataCollectingTypeFactory,
    FlexibleAttributeForPDUFactory,
    PeriodicFieldDataFactory,
    create_afghanistan,
    create_ukraine,
)
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import BeneficiaryGroupFactory, ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from models.account import AdminAreaLimitedTo
from hope.apps.account.permissions import Permissions
from models.core import (
    DataCollectingType,
    FlexibleAttribute,
    PeriodicFieldData,
)
from models.program import Program

pytestmark = pytest.mark.django_db


class TestProgramCopy:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.dct_original = DataCollectingTypeFactory(
            label="Original DCT",
            code="origdct",
            type=DataCollectingType.Type.STANDARD,
            active=True,
        )
        self.dct_compatible = DataCollectingTypeFactory(
            label="Compatible DCT",
            code="compdct",
            type=DataCollectingType.Type.STANDARD,
            active=True,
        )
        self.dct_incompatible = DataCollectingTypeFactory(
            label="Incompatible DCT",
            code="incompdct",
            type=DataCollectingType.Type.SOCIAL,
            active=True,
        )
        self.dct_original.compatible_types.add(self.dct_compatible)

        self.bg_original = BeneficiaryGroupFactory(name="Original BG", master_detail=True)

        self.program_to_copy = ProgramFactory(
            business_area=self.afghanistan,
            name="Test Program To Copy",
            description="Test Program To Copy Description",
            status=Program.ACTIVE,
            programme_code="ORIG",
            data_collecting_type=self.dct_original,
            beneficiary_group=self.bg_original,
            sector=Program.EDUCATION,
            start_date=datetime.date(2023, 1, 1),
            end_date=datetime.date(2023, 12, 31),
            partner_access=Program.NONE_PARTNERS_ACCESS,
            budget=100,
            population_goal=10,
            cash_plus=False,
            frequency_of_payments=Program.REGULAR,
            administrative_areas_of_implementation="Original areas impl.",
        )

        self.copy_url = reverse(
            "api:programs:programs-copy",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program_to_copy.slug,
            },
        )

        pdu_data = PeriodicFieldDataFactory(subtype=PeriodicFieldData.STRING, number_of_rounds=1, rounds_names=["R1"])
        FlexibleAttributeForPDUFactory(program=self.program_to_copy, label="Original PDU1", pdu_data=pdu_data)

        create_household_and_individuals(
            household_data={
                "program": self.program_to_copy,
                "business_area": self.afghanistan,
            },
            individuals_data=[{"business_area": self.afghanistan}],
        )

        self.partner1_for_assign = PartnerFactory(name="Partner 1")
        self.partner2_for_assign = PartnerFactory(name="Partner 2")

        self.partner.allowed_business_areas.set([self.afghanistan])
        self.partner1_for_assign.allowed_business_areas.set([self.afghanistan])
        self.partner2_for_assign.allowed_business_areas.set([self.afghanistan])

        # TODO: Temporary solution - remove the below after proper solution is applied
        RoleAssignmentFactory(
            partner=self.partner,
            business_area=self.afghanistan,
            program=None,
        )
        RoleAssignmentFactory(
            partner=self.partner1_for_assign,
            business_area=self.afghanistan,
            program=None,
        )
        RoleAssignmentFactory(
            partner=self.partner2_for_assign,
            business_area=self.afghanistan,
            program=None,
        )
        # TODO: remove the above after proper solution is applied

        country = CountryFactory()
        country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=country, area_level=1)
        self.area1 = AreaFactory(parent=None, area_type=admin_type, p_code="AFCPY1", name="AreaCopy1")
        self.area2 = AreaFactory(parent=None, area_type=admin_type, p_code="AFCPY2", name="AreaCopy2")

        self.base_copy_payload = {
            "name": "Copied Program Name",
            "programme_code": "COPY",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "sector": Program.HEALTH,
            "description": "Description for copied program.",
            "budget": 50000,
            "administrative_areas_of_implementation": "New areas impl.",
            "population_goal": 50,
            "cash_plus": True,
            "frequency_of_payments": Program.ONE_OFF,
            "data_collecting_type": self.dct_compatible.code,
            "partner_access": Program.NONE_PARTNERS_ACCESS,
            "partners": [],
            "pdu_fields": [
                {
                    "label": "New PDU For Copy",
                    "pdu_data": {
                        "subtype": PeriodicFieldData.BOOL,
                        "number_of_rounds": 1,
                        "rounds_names": ["R1C"],
                    },
                }
            ],
        }

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_DUPLICATE], status.HTTP_201_CREATED),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_copy_program_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Callable,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)
        response = self.client.post(self.copy_url, self.base_copy_payload)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_201_CREATED:
            new_program = Program.objects.get(name="Copied Program Name", business_area=self.afghanistan)
            assert response.json() == {"message": f"Program copied successfully. New Program slug: {new_program.slug}"}

    def test_copy_program(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.client.post(self.copy_url, self.base_copy_payload)
        assert response.status_code == status.HTTP_201_CREATED

        new_program_slug = response.json()["message"].split(": ")[-1]
        new_program = Program.objects.get(slug=new_program_slug, business_area=self.afghanistan)

        # Check copied fields
        assert new_program.name == "Copied Program Name"
        assert new_program.programme_code == "COPY"
        assert new_program.slug == "copy"
        assert new_program.start_date == datetime.date(2024, 1, 1)
        assert new_program.end_date == datetime.date(2024, 12, 31)
        assert new_program.sector == Program.HEALTH
        assert new_program.description == "Description for copied program."
        assert new_program.budget == 50000
        assert new_program.administrative_areas_of_implementation == "New areas impl."
        assert new_program.population_goal == 50
        assert new_program.cash_plus is True
        assert new_program.frequency_of_payments == Program.ONE_OFF
        assert new_program.data_collecting_type.code == self.dct_compatible.code
        assert str(new_program.beneficiary_group.id) == str(self.bg_original.id)
        assert new_program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert new_program.status == Program.DRAFT  # New program should be in DRAFT status

        # Check PDU fields
        pdu_fields = FlexibleAttribute.objects.filter(program=new_program)
        assert pdu_fields.count() == 1
        pdu_field = pdu_fields.first()
        assert pdu_field.label["English(EN)"] == "New PDU For Copy"
        assert pdu_field.pdu_data.subtype == PeriodicFieldData.BOOL
        assert pdu_field.pdu_data.number_of_rounds == 1
        assert pdu_field.pdu_data.rounds_names == ["R1C"]

        # Check that the original program's data is not modified
        original_program = Program.objects.get(id=self.program_to_copy.id)
        assert original_program.name == "Test Program To Copy"
        assert original_program.programme_code == "ORIG"
        assert original_program.slug == "orig"
        assert original_program.start_date == datetime.date(2023, 1, 1)
        assert original_program.end_date == datetime.date(2023, 12, 31)
        assert original_program.description == "Test Program To Copy Description"
        assert original_program.budget == 100
        assert original_program.population_goal == 10
        assert original_program.administrative_areas_of_implementation == "Original areas impl."
        assert original_program.cash_plus is False
        assert original_program.frequency_of_payments == Program.REGULAR
        assert original_program.sector == Program.EDUCATION
        assert original_program.data_collecting_type.code == self.dct_original.code
        assert str(original_program.beneficiary_group.id) == str(self.bg_original.id)
        assert original_program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert original_program.status == Program.ACTIVE
        pdu_fields_original = FlexibleAttribute.objects.filter(program=self.program_to_copy)
        assert pdu_fields_original.count() == 1
        pdu_field_original = pdu_fields_original.first()
        assert pdu_field_original.label["English(EN)"] == "Original PDU1"
        assert pdu_field_original.pdu_data.subtype == PeriodicFieldData.STRING
        assert pdu_field_original.pdu_data.number_of_rounds == 1
        assert pdu_field_original.pdu_data.rounds_names == ["R1"]

    def test_copy_program_new_programme_code_generation(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "programme_code": None,
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        new_program_slug = response.json()["message"].split(": ")[-1]
        new_program = Program.objects.get(slug=new_program_slug, business_area=self.afghanistan)
        assert new_program.programme_code != self.program_to_copy.programme_code
        assert new_program.slug != self.program_to_copy.slug

    def test_copy_program_existing_programme_code(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "programme_code": self.program_to_copy.programme_code,
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert "programme_code" in response.json()
        assert response.json()["programme_code"][0] == "Programme code is already used."

    def test_copy_program_invalid_programme_code(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "programme_code": "T#ST",
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert "programme_code" in response.json()
        assert (
            "Programme code should be exactly 4 characters long and may only contain letters, digits and character: -"
            in response.json()["programme_code"][0]
        )

    def test_copy_program_with_invalid_dates(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "start_date": "2024-12-31",
            "end_date": "2024-01-01",
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert "end_date" in response.json()
        assert "End date cannot be earlier than the start date." in response.json()["end_date"][0]

    def test_copy_program_incompatible_dct(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "data_collecting_type": self.dct_incompatible.code,
        }

        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response.json()
        assert (
            "Data Collecting Type must be compatible with the original Program."
            in response.json()["data_collecting_type"][0]
        )

    def test_copy_program_dct_invalid(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        payload = {
            **self.base_copy_payload,
            "data_collecting_type": self.dct_compatible.code,
        }

        # DCT inactive
        self.dct_compatible.active = False
        self.dct_compatible.save()
        response_for_inactive = self.client.post(self.copy_url, payload)
        assert response_for_inactive.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_inactive.json()
        assert (
            response_for_inactive.json()["data_collecting_type"][0]
            == "Only active Data Collecting Type can be used in Program."
        )

        # DCT deprecated
        self.dct_compatible.active = True
        self.dct_compatible.deprecated = True
        self.dct_compatible.save()
        response_for_deprecated = self.client.post(self.copy_url, payload)
        assert response_for_deprecated.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_deprecated.json()
        assert (
            response_for_deprecated.json()["data_collecting_type"][0]
            == "Deprecated Data Collecting Type cannot be used in Program."
        )

        # DCT limited to another BA
        self.dct_compatible.deprecated = False
        self.dct_compatible.save()
        ukraine = create_ukraine()
        self.dct_compatible.limit_to.add(ukraine)
        response_for_limited = self.client.post(self.copy_url, payload)
        assert response_for_limited.status_code == status.HTTP_400_BAD_REQUEST
        assert "data_collecting_type" in response_for_limited.json()
        assert (
            response_for_limited.json()["data_collecting_type"][0]
            == "This Data Collecting Type is not available for this Business Area."
        )

    def test_copy_program_all_partners_access(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "partner_access": Program.ALL_PARTNERS_ACCESS,
        }

        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        new_program_slug = response.json()["message"].split(": ")[-1]
        new_program = Program.objects.get(slug=new_program_slug, business_area=self.afghanistan)
        assert new_program.partner_access == Program.ALL_PARTNERS_ACCESS
        assert new_program.role_assignments.count() == 3
        assert set(new_program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assign.id,
            self.partner2_for_assign.id,
        }

    def test_copy_program_all_partners_access_with_partners_data(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "partner_access": Program.ALL_PARTNERS_ACCESS,
            "partners": [
                {"partner": str(self.partner.id), "areas": [str(self.area1.id)]},
                {"partner": str(self.partner2_for_assign.id), "areas": []},
            ],
        }

        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert "You cannot specify partners for the chosen access type." in response.json()["partners"][0]

    def test_copy_program_none_partners_access_with_partners_data(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "partner_access": Program.NONE_PARTNERS_ACCESS,
            "partners": [
                {"partner": str(self.partner.id), "areas": [str(self.area1.id)]},
                {"partner": str(self.partner2_for_assign.id), "areas": []},
            ],
        }

        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert "You cannot specify partners for the chosen access type." in response.json()["partners"][0]

    def test_copy_program_selected_access(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {"partner": str(self.partner.id), "areas": [str(self.area1.id)]},
                {"partner": str(self.partner2_for_assign.id), "areas": []},
            ],
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_201_CREATED

        new_program_slug = response.json()["message"].split(": ")[-1]
        new_program = Program.objects.get(slug=new_program_slug, business_area=self.afghanistan)
        assert new_program.partner_access == Program.SELECTED_PARTNERS_ACCESS
        assert new_program.role_assignments.count() == 2
        assert set(new_program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner2_for_assign.id,
        }
        assert AdminAreaLimitedTo.objects.filter(program=new_program).count() == 1
        assert (
            AdminAreaLimitedTo.objects.filter(
                program=new_program,
                partner=self.partner,
            ).count()
            == 1
        )
        assert (
            AdminAreaLimitedTo.objects.filter(
                program=new_program,
                partner=self.partner2_for_assign,
            ).count()
            == 0
        )

    def test_copy_program_selected_access_without_partner(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_DUPLICATE],
            self.afghanistan,
            whole_business_area_access=True,
        )

        payload = {
            **self.base_copy_payload,
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner1_for_assign.id),
                    "areas": [str(self.area1.id)],
                },
                {"partner": str(self.partner2_for_assign.id), "areas": []},
            ],
        }
        response = self.client.post(self.copy_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        assert "partners" in response.json()
        assert "Please assign access to your partner before saving the Program." in response.json()["partners"][0]
