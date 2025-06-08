from typing import Callable, List, Dict, Any
import copy
import datetime

import pytest
from django.db.models import Q
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import (
    UserFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
)
from hct_mis_api.apps.account.models import Partner, RoleAssignment, AdminAreaLimitedTo
from hct_mis_api.apps.account.permissions import Permissions
from hct_mis_api.apps.core.fixtures import (
    create_afghanistan, 
    DataCollectingTypeFactory, 
    PeriodicFieldDataFactory,
    FlexibleAttributeForPDUFactory,
    create_ukraine,
)
from hct_mis_api.apps.program.fixtures import ProgramFactory, BeneficiaryGroupFactory, ProgramCycleFactory
from hct_mis_api.apps.program.models import Program, ProgramCycle, BeneficiaryGroup
from hct_mis_api.apps.geo.fixtures import AreaFactory, AreaTypeFactory, CountryFactory
from hct_mis_api.apps.geo.models import Area
from hct_mis_api.apps.core.models import DataCollectingType, FlexibleAttribute, PeriodicFieldData
from hct_mis_api.apps.household.fixtures import create_household_and_individuals
from hct_mis_api.apps.household.models import Household, Individual


pytestmark = pytest.mark.django_db


class TestProgramCopy:
    @pytest.fixture(autouse=True)
    def setup(self, api_client) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.dct_original = DataCollectingTypeFactory(label="Original DCT", code="origdct", type=DataCollectingType.Type.STANDARD, active=True)
        self.dct_compatible = DataCollectingTypeFactory(label="Compatible DCT", code="compdct", type=DataCollectingType.Type.STANDARD, active=True)
        self.dct_incompatible = DataCollectingTypeFactory(label="Incompatible DCT", code="incompdct", type=DataCollectingType.Type.SOCIAL, active=True)
        self.dct_original.compatible_types.add(self.dct_compatible)

        self.bg_original = BeneficiaryGroupFactory(name="Original BG", master_detail=True)
        self.bg_compatible_with_dct_compatible = BeneficiaryGroupFactory(name="Compatible BG for Comp DCT", master_detail=True)
        self.bg_incompatible_with_dct_compatible = BeneficiaryGroupFactory(name="Incompatible BG for Comp DCT", master_detail=False)


        self.program_to_copy = ProgramFactory(
            business_area=self.afghanistan,
            name="Test Program To Copy",
            description="Test Program To Copy Description",
            status=Program.ACTIVE,
            programme_code="ORIG",
            data_collecting_type=self.dct_original,
            beneficiary_group=self.bg_original,
            sector= Program.EDUCATION,
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
            kwargs={"business_area_slug": self.afghanistan.slug, "slug": self.program_to_copy.slug},
        )

        pdu_data = PeriodicFieldDataFactory(subtype=PeriodicFieldData.STRING, number_of_rounds=1, rounds_names=["R1"])
        FlexibleAttributeForPDUFactory(program=self.program_to_copy, label="Original PDU1", pdu_data=pdu_data)

        create_household_and_individuals(
            household_data={"program": self.program_to_copy, "business_area": self.afghanistan},
            individuals_data=[{"business_area": self.afghanistan}]
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
            "beneficiary_group": str(self.bg_compatible_with_dct_compatible.id),
            "partner_access": Program.NONE_PARTNERS_ACCESS,
            "partners": [],
            "pdu_fields": [
                {
                    "label": "New PDU For Copy", 
                    "pdu_data": {"subtype": PeriodicFieldData.BOOL, "number_of_rounds": 1, "rounds_names": ["R1C"]}
                }
            ]
        }

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.PROGRAMME_DUPLICATE], status.HTTP_201_CREATED),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_copy_program_permissions(
        self, permissions: list, expected_status: int, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)
        response = self.client.post(self.copy_url, self.base_copy_payload)
        assert response.status_code == expected_status

        if expected_status == status.HTTP_201_CREATED:
            new_program = Program.objects.get(name="Copied Program Name", business_area=self.afghanistan)
            assert response.json() == {"message": f"Program copied successfully. New Program slug: {new_program.slug}"}

    def test_copy_program(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_DUPLICATE], self.afghanistan, whole_business_area_access=True)

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
        assert str(new_program.beneficiary_group.id) == str(self.bg_compatible_with_dct_compatible.id)
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
