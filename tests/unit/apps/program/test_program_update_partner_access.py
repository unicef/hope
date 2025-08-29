from typing import Any, Callable

from django.db.models import Q
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import (
    PartnerFactory,
    RoleAssignmentFactory,
    UserFactory,
)
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.geo import AreaFactory, AreaTypeFactory, CountryFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.models.admin_area_limited_to import AdminAreaLimitedTo
from hope.models.role_assignment import RoleAssignment
from hope.apps.account.permissions import Permissions
from hope.models.program import Program

pytestmark = pytest.mark.django_db


class TestProgramUpdatePartnerAccess:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            partner_access=Program.NONE_PARTNERS_ACCESS,
            name="Test Program for Partner Access",
        )

        self.partner1_for_assignment = PartnerFactory(name="Test Partner 1")
        self.partner2_for_assignment = PartnerFactory(name="Test Partner 2")
        self.unicef_partner = PartnerFactory(name="UNICEF")
        self.unicef_hq = PartnerFactory(name="UNICEF HQ", parent=self.unicef_partner)
        self.unicef_partner_in_afghanistan = PartnerFactory(
            name="UNICEF Partner for afghanistan", parent=self.unicef_partner
        )

        # partners have to be allowed in BA to be able to be assigned to program
        self.partner.allowed_business_areas.add(self.afghanistan)
        self.partner1_for_assignment.allowed_business_areas.add(self.afghanistan)
        self.partner2_for_assignment.allowed_business_areas.add(self.afghanistan)

        country = CountryFactory()
        country.business_areas.set([self.afghanistan])
        admin_type = AreaTypeFactory(country=country, area_level=1)
        self.area1 = AreaFactory(parent=None, area_type=admin_type, p_code="AF01", name="Area1")
        self.area2 = AreaFactory(parent=None, area_type=admin_type, p_code="AF02", name="Area2")

        self.update_partner_access_url = reverse(
            "api:programs:programs-update-partner-access",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program.slug,
            },
        )

        self.base_expected_response = {
            "partners": [
                {
                    "id": self.partner.id,
                    "name": self.partner.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_hq.id,
                    "name": self.unicef_hq.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
                {
                    "id": self.unicef_partner_in_afghanistan.id,
                    "name": self.unicef_partner_in_afghanistan.name,
                    "areas": [
                        {
                            "id": str(self.area1.id),
                            "level": self.area1.level,
                        },
                        {
                            "id": str(self.area2.id),
                            "level": self.area2.level,
                        },
                    ],
                    "area_access": "BUSINESS_AREA",
                },
            ],
        }

        # TODO: due to temporary solution in program mutations,
        # Partners need to already have a role in the BA to be able to be granted access to program
        # (created role in program is the same role as the Partner already held in the BA.
        # For each held role, the same role is now applied for the new program.
        # After removing this solution, below lines of setup can be deleted.
        # The Role for RoleAssignment will be passed in input.

        # TODO: the below code is needed due to the temporary solution on the partners access in program actions
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, program=None)
        RoleAssignmentFactory(
            partner=self.partner1_for_assignment,
            business_area=self.afghanistan,
            program=None,
        )
        RoleAssignmentFactory(
            partner=self.partner2_for_assignment,
            business_area=self.afghanistan,
            program=None,
        )
        # TODO: remove the above code when the partners access in program actions is implemented properly
        # TODO: also add tests for cases when partner is not allowed in BA - also in test create program

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_UPDATE], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_partner_access_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Callable,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        payload = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == expected_status

        self.program.refresh_from_db()
        if expected_status == status.HTTP_200_OK:
            assert self.program.partner_access == Program.ALL_PARTNERS_ACCESS
            assert response.json() == {"message": "Partner access updated."}
            assert (
                self.program.role_assignments.count() == 3
            )  # roles created for self.partner, self.partner1_for_assignment, self.partner2_for_assignment
            assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
                self.partner.id,
                self.partner1_for_assignment.id,
                self.partner2_for_assignment.id,
            }
        else:
            assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS  # Should not change if permission denied

    def test_update_partner_access(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0
        # UNICEF HQ and UNICEF Partner for Afghanistan have Role in the whole BA
        assert (
            RoleAssignment.objects.filter(
                Q(partner=self.unicef_hq) | Q(partner=self.unicef_partner_in_afghanistan),
                business_area=self.afghanistan,
                program=None,
            ).count()
            == 2
        )
        assert (
            self.unicef_hq.role_assignments.filter(program=None, business_area=self.program.business_area)
            .first()
            .role.name
            == "Role with all permissions"
        )
        assert (
            self.unicef_partner_in_afghanistan.role_assignments.filter(
                program=None, business_area=self.program.business_area
            )
            .first()
            .role.name
            == "Role for UNICEF Partners"
        )

        # Update partner access NONE_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
        payload_1 = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
        response = self.client.post(self.update_partner_access_url, payload_1)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.ALL_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 3
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
            self.partner2_for_assignment.id,
        }

        # Update partner access ALL_PARTNERS_ACCESS -> NONE_PARTNERS_ACCESS
        payload_2 = {"partner_access": Program.NONE_PARTNERS_ACCESS, "partners": []}
        response = self.client.post(self.update_partner_access_url, payload_2)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        # Update partner access NONE_PARTNERS_ACCESS -> SELECTED_PARTNERS_ACCESS with specific partners
        payload_3 = {
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner.id),
                    "areas": [str(self.area1.id)],
                },
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload_3)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.SELECTED_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 2
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
        }
        assert AdminAreaLimitedTo.objects.filter(program=self.program).count() == 1
        assert AdminAreaLimitedTo.objects.filter(partner=self.partner, program=self.program).count() == 1
        assert (
            AdminAreaLimitedTo.objects.filter(partner=self.partner1_for_assignment, program=self.program).count() == 0
        )

        # Update partners for SELECTED_PARTNERS_ACCESS - add partner, change areas
        payload_4 = {
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner.id),
                    "areas": [str(self.area2.id)],
                },
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [str(self.area2.id)],
                },
                {
                    "partner": str(self.partner2_for_assignment.id),
                    "areas": [],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload_4)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.SELECTED_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 3
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
            self.partner2_for_assignment.id,
        }
        assert AdminAreaLimitedTo.objects.filter(program=self.program).count() == 2
        assert AdminAreaLimitedTo.objects.filter(partner=self.partner, program=self.program).count() == 1
        assert (
            AdminAreaLimitedTo.objects.filter(partner=self.partner1_for_assignment, program=self.program).count() == 1
        )
        assert (
            AdminAreaLimitedTo.objects.filter(partner=self.partner2_for_assignment, program=self.program).count() == 0
        )

        # Update partners and areas for SELECTED_PARTNERS_ACCESS - remove one of partners, change areas
        payload_5 = {
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner.id),
                    "areas": [str(self.area2.id)],
                },
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [str(self.area2.id)],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload_5)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.SELECTED_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 2
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
        }
        assert AdminAreaLimitedTo.objects.filter(program=self.program).count() == 2
        assert AdminAreaLimitedTo.objects.filter(partner=self.partner, program=self.program).count() == 1
        assert (
            AdminAreaLimitedTo.objects.filter(partner=self.partner1_for_assignment, program=self.program).count() == 1
        )
        assert (
            AdminAreaLimitedTo.objects.filter(partner=self.partner2_for_assignment, program=self.program).count() == 0
        )

        # Update partner access SELECTED_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
        payload_6 = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
        response = self.client.post(self.update_partner_access_url, payload_6)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.ALL_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 3
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
            self.partner2_for_assignment.id,
        }
        assert AdminAreaLimitedTo.objects.filter(program=self.program).count() == 0

    def test_update_partner_access_invalid_all_partners_access_with_partners_data(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        payload = {
            "partner_access": Program.ALL_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [str(self.area2.id)],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."

        self.program.refresh_from_db()
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

    def test_update_partner_access_invalid_none_partners_access_with_partners_data(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        payload = {
            "partner_access": Program.NONE_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [str(self.area2.id)],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert response.json()["partners"][0] == "You cannot specify partners for the chosen access type."

        self.program.refresh_from_db()
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

    def test_update_partner_access_invalid_selected_partner_access_without_partner(
        self, create_user_role_with_permissions: Callable
    ) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        # Update partner access NONE_PARTNERS_ACCESS -> SELECTED_PARTNERS_ACCESS without the current partner
        payload = {
            "partner_access": Program.SELECTED_PARTNERS_ACCESS,
            "partners": [
                {
                    "partner": str(self.partner1_for_assignment.id),
                    "areas": [str(self.area2.id)],
                },
            ],
        }
        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "partners" in response.json()
        assert response.json()["partners"][0] == "Please assign access to your partner before saving the Program."

        self.program.refresh_from_db()
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

    def test_update_partner_access_all_partners_refresh(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_UPDATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        assert self.program.partner_access == Program.NONE_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 0

        # Update partner access NONE_PARTNERS_ACCESS -> ALL_PARTNERS_ACCESS
        payload = {"partner_access": Program.ALL_PARTNERS_ACCESS, "partners": []}
        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.ALL_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 3

        # new partner allowed in BA
        partner_new = PartnerFactory(name="Test Partner New")
        partner_new.allowed_business_areas.add(self.afghanistan)

        # TODO: temporary solution to remove below
        RoleAssignmentFactory(partner=partner_new, business_area=self.afghanistan, program=None)
        # TODO: remove above when the partners access in program actions is implemented properly

        response = self.client.post(self.update_partner_access_url, payload)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Partner access updated."}
        self.program.refresh_from_db()
        assert self.program.partner_access == Program.ALL_PARTNERS_ACCESS
        assert self.program.role_assignments.count() == 4
        assert set(self.program.role_assignments.values_list("partner", flat=True)) == {
            self.partner.id,
            self.partner1_for_assignment.id,
            self.partner2_for_assignment.id,
            partner_new.id,
        }
