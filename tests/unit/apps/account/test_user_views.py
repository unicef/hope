import json
from typing import Any

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.fixtures import PartnerFactory, UserFactory, RoleAssignmentFactory, RoleFactory
from hct_mis_api.apps.account.permissions import Permissions, ALL_GRIEVANCES_CREATE_MODIFY
from hct_mis_api.apps.accountability.fixtures import SurveyFactory, FeedbackFactory
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.fixtures import create_afghanistan, create_ukraine
from hct_mis_api.apps.grievance.fixtures import GrievanceTicketFactory
from hct_mis_api.apps.program.fixtures import ProgramFactory
from hct_mis_api.apps.program.models import Program
from tests.selenium.conftest import business_area
from hct_mis_api.apps.account.models import Role, INACTIVE
from tests.unit.fixtures import create_user_role_with_permissions
from hct_mis_api.apps.core.models import BusinessArea

pytestmark = pytest.mark.django_db


def get_role_data(role: Role) -> dict:
    return {
        "name": role.name,
        "subsystem": role.subsystem,
        "created_at": f"{role.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
        "updated_at": f"{role.updated_at:%Y-%m-%dT%H:%M:%S.%fZ}",
        "permissions": [str(perm) for perm in role.permissions],
        "is_visible_on_ui": role.is_visible_on_ui,
        "is_available_for_partner": role.is_available_for_partner,
    }

def get_business_area_data(business_area: BusinessArea) -> dict:
    return {
        "id": str(business_area.id),
        "name": business_area.name,
        "slug": business_area.slug,
        "is_accountability_applicable": False,
    }

class TestUserProfile:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.afghanistan.active = True
        self.afghanistan.save()

        self.program1 = ProgramFactory(business_area=self.afghanistan, name="Program1", status=Program.ACTIVE)
        self.program2 = ProgramFactory(business_area=self.afghanistan, name="Program2", status=Program.ACTIVE)
        self.program3 = ProgramFactory(business_area=self.afghanistan, name="Program3", status=Program.ACTIVE)

        self.partner = PartnerFactory(name="Test Partner")

        self.user_profile_url = reverse(
            "api:accounts:users-profile",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )

        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.role1 = RoleFactory(name="TestRole1", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value, Permissions.PROGRAMME_FINISH.value])
        self.role2 = RoleFactory(name="TestRole2", permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value])
        self.role3 = RoleFactory(name="TestRole3", permissions=[Permissions.TARGETING_VIEW_LIST.value])
        self.role4 = RoleFactory(name="TestRole4", permissions=[Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE.value])
        self.role_p1 = RoleFactory(name="TestRoleP1", permissions=[Permissions.PM_CREATE.value, Permissions.PM_VIEW_LIST.value])
        self.role_p2 = RoleFactory(name="TestRoleP2", permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE.value])
        self.role_p3 = RoleFactory(name="TestRoleP3", permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST.value])

        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, role=self.role1)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program1, role=self.role2)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program2, role=self.role3)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program3, role=self.role4)
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, role=self.role_p1)
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, program=self.program1, role=self.role_p2)
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, program=self.program2, role=self.role_p3)

        # role in different BA
        ukraine = create_ukraine()
        ukraine.active = True
        ukraine.save()
        program_u = ProgramFactory(business_area=ukraine, status=Program.ACTIVE)
        RoleAssignmentFactory(user=self.user, business_area=ukraine, program=program_u, role=self.role1)
        RoleAssignmentFactory(partner=self.partner, business_area=ukraine, role=self.role_p1)


    def test_user_profile_in_scope_business_area(self) -> None:
        response = self.api_client.get(self.user_profile_url)
        assert response.status_code == status.HTTP_200_OK

        profile_data = response.data
        assert profile_data["id"] == str(self.user.id)
        assert profile_data["username"] == self.user.username
        assert profile_data["email"] == self.user.email
        assert profile_data["first_name"] == self.user.first_name
        assert profile_data["last_name"] == self.user.last_name
        assert profile_data["is_superuser"] == self.user.is_superuser
        assert profile_data["partner"] == {
            "id": self.partner.id,
            "name": self.partner.name,
        }
        assert profile_data["partner_roles"] == [
            get_role_data(self.role_p1),
            get_role_data(self.role_p2),
            get_role_data(self.role_p3),
        ]

        assert profile_data["user_roles"] == [
            get_role_data(self.role1),
            get_role_data(self.role2),
            get_role_data(self.role3),
            get_role_data(self.role4),
        ]
        assert profile_data["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in [*self.role1.permissions, *self.role2.permissions, *self.role3.permissions, *self.role4.permissions, *self.role_p1.permissions, *self.role_p2.permissions, *self.role_p3.permissions]},
            }
        ]

        assert profile_data["permissions_in_scope"] == {str(perm) for perm in [*self.role1.permissions, *self.role2.permissions, *self.role3.permissions, *self.role4.permissions, *self.role_p1.permissions, *self.role_p2.permissions, *self.role_p3.permissions]}

    def test_user_profile_in_scope_program(self) -> None:
        response = self.api_client.get(self.user_profile_url, {"program": self.program1.id})
        assert response.status_code == status.HTTP_200_OK

        profile_data = response.data
        assert profile_data["id"] == str(self.user.id)
        assert profile_data["username"] == self.user.username
        assert profile_data["email"] == self.user.email
        assert profile_data["first_name"] == self.user.first_name
        assert profile_data["last_name"] == self.user.last_name
        assert profile_data["is_superuser"] == self.user.is_superuser
        assert profile_data["partner"] == {
            "id": self.partner.id,
            "name": self.partner.name,
        }

        assert profile_data["partner_roles"] == [
            get_role_data(self.role_p1),
            get_role_data(self.role_p2),
            get_role_data(self.role_p3),
        ]

        assert profile_data["user_roles"] == [
            get_role_data(self.role1),
            get_role_data(self.role2),
            get_role_data(self.role3),
            get_role_data(self.role4),
        ]
        assert profile_data["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in [*self.role1.permissions, *self.role2.permissions, *self.role3.permissions, *self.role4.permissions, *self.role_p1.permissions, *self.role_p2.permissions, *self.role_p3.permissions]},
            }
        ]

        # change here - only permissions within the program
        assert profile_data["permissions_in_scope"] == {str(perm) for perm in [*self.role1.permissions, *self.role2.permissions, *self.role_p1.permissions, *self.role_p2.permissions]}


