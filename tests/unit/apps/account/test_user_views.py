import datetime
import json
from typing import Any

from django.core.cache import cache
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

import pytest
from extras.test_utils.factories.account import (
    AdminAreaLimitedToFactory,
    PartnerFactory,
    RoleAssignmentFactory,
    RoleFactory,
    UserFactory,
)
from extras.test_utils.factories.accountability import FeedbackFactory, SurveyFactory
from extras.test_utils.factories.core import create_afghanistan, create_ukraine
from extras.test_utils.factories.geo import AreaFactory
from extras.test_utils.factories.grievance import GrievanceTicketFactory
from extras.test_utils.factories.household import create_household_and_individuals
from extras.test_utils.factories.program import ProgramFactory
from rest_framework import status
from rest_framework.reverse import reverse

from hct_mis_api.apps.account.models import INACTIVE, USER_STATUS_CHOICES, Partner, Role
from hct_mis_api.apps.account.permissions import (
    ALL_GRIEVANCES_CREATE_MODIFY,
    Permissions,
)
from hct_mis_api.apps.accountability.models import Message
from hct_mis_api.apps.core.models import BusinessArea
from hct_mis_api.apps.core.utils import to_choice_object
from hct_mis_api.apps.program.models import Program

pytestmark = pytest.mark.django_db


def get_role_data(role: Role) -> dict:
    return {
        "name": role.name,
        "subsystem": role.subsystem,
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

        self.user = UserFactory(
            partner=self.partner, last_login=timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d"))
        )
        self.api_client = api_client(self.user)

        self.role1 = RoleFactory(
            name="TestRole1",
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value, Permissions.PROGRAMME_FINISH.value],
        )
        self.role2 = RoleFactory(name="TestRole2", permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value])
        self.role3 = RoleFactory(name="TestRole3", permissions=[Permissions.TARGETING_VIEW_LIST.value])
        self.role4 = RoleFactory(name="TestRole4", permissions=[Permissions.GRIEVANCES_FEEDBACK_VIEW_UPDATE.value])
        self.role_p1 = RoleFactory(
            name="TestRoleP1", permissions=[Permissions.PM_CREATE.value, Permissions.PM_VIEW_LIST.value]
        )
        self.role_p2 = RoleFactory(name="TestRoleP2", permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE.value])
        self.role_p3 = RoleFactory(name="TestRoleP3", permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_LIST.value])

        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, role=self.role1)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program1, role=self.role2)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program2, role=self.role3)
        RoleAssignmentFactory(user=self.user, business_area=self.afghanistan, program=self.program3, role=self.role4)
        RoleAssignmentFactory(partner=self.partner, business_area=self.afghanistan, role=self.role_p1)
        RoleAssignmentFactory(
            partner=self.partner, business_area=self.afghanistan, program=self.program1, role=self.role_p2
        )
        RoleAssignmentFactory(
            partner=self.partner, business_area=self.afghanistan, program=self.program2, role=self.role_p3
        )

        # role in different BA
        self.ukraine = create_ukraine()
        self.ukraine.active = True
        self.ukraine.save()
        self.program_u = ProgramFactory(business_area=self.ukraine, status=Program.ACTIVE)
        RoleAssignmentFactory(user=self.user, business_area=self.ukraine, program=self.program_u, role=self.role1)
        RoleAssignmentFactory(partner=self.partner, business_area=self.ukraine, role=self.role_p1)

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
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role_p1),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program1.name,
                "role": get_role_data(self.role_p2),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program2.name,
                "role": get_role_data(self.role_p3),
            },
            {
                "business_area": self.ukraine.slug,
                "program": None,
                "role": get_role_data(self.role_p1),
            },
        ]

        assert profile_data["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role1),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program1.name,
                "role": get_role_data(self.role2),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program2.name,
                "role": get_role_data(self.role3),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program3.name,
                "role": get_role_data(self.role4),
            },
            {
                "business_area": self.ukraine.slug,
                "program": self.program_u.name,
                "role": get_role_data(self.role1),
            },
        ]
        assert profile_data["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {
                    str(perm)
                    for perm in [
                        *self.role1.permissions,
                        *self.role2.permissions,
                        *self.role3.permissions,
                        *self.role4.permissions,
                        *self.role_p1.permissions,
                        *self.role_p2.permissions,
                        *self.role_p3.permissions,
                    ]
                },
            },
            {
                **get_business_area_data(self.ukraine),
                "permissions": {
                    str(perm)
                    for perm in [
                        *self.role1.permissions,
                        *self.role_p1.permissions,
                    ]
                },
            },
        ]

        assert profile_data["permissions_in_scope"] == {
            str(perm)
            for perm in [
                *self.role1.permissions,
                *self.role2.permissions,
                *self.role3.permissions,
                *self.role4.permissions,
                *self.role_p1.permissions,
                *self.role_p2.permissions,
                *self.role_p3.permissions,
            ]
        }
        assert profile_data["cross_area_filter_available"] is False

        assert profile_data["status"] == self.user.status
        assert profile_data["last_login"] == f"{self.user.last_login:%Y-%m-%dT%H:%M:%SZ}"

    def test_user_profile_in_scope_program(self) -> None:
        response = self.api_client.get(self.user_profile_url, {"program": self.program1.slug})
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
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role_p1),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program1.name,
                "role": get_role_data(self.role_p2),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program2.name,
                "role": get_role_data(self.role_p3),
            },
            {
                "business_area": self.ukraine.slug,
                "program": None,
                "role": get_role_data(self.role_p1),
            },
        ]

        assert profile_data["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role1),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program1.name,
                "role": get_role_data(self.role2),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program2.name,
                "role": get_role_data(self.role3),
            },
            {
                "business_area": self.afghanistan.slug,
                "program": self.program3.name,
                "role": get_role_data(self.role4),
            },
            {
                "business_area": self.ukraine.slug,
                "program": self.program_u.name,
                "role": get_role_data(self.role1),
            },
        ]

        assert profile_data["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {
                    str(perm)
                    for perm in [
                        *self.role1.permissions,
                        *self.role2.permissions,
                        *self.role3.permissions,
                        *self.role4.permissions,
                        *self.role_p1.permissions,
                        *self.role_p2.permissions,
                        *self.role_p3.permissions,
                    ]
                },
            },
            {
                **get_business_area_data(self.ukraine),
                "permissions": {
                    str(perm)
                    for perm in [
                        *self.role1.permissions,
                        *self.role_p1.permissions,
                    ]
                },
            },
        ]

        # change here - only permissions within the program
        assert profile_data["permissions_in_scope"] == {
            str(perm)
            for perm in [
                *self.role1.permissions,
                *self.role2.permissions,
                *self.role_p1.permissions,
                *self.role_p2.permissions,
            ]
        }
        assert profile_data["cross_area_filter_available"] is False

    @pytest.mark.parametrize(
        "permissions, filter_available",
        [
            ([Permissions.GRIEVANCES_CROSS_AREA_FILTER], True),
            ([], False),
        ],
    )
    def test_cross_area_filter_available_in_scope_business_area(
        self,
        permissions: list,
        filter_available: bool,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(self.user_profile_url)
        assert response.status_code == status.HTTP_200_OK

        profile_data = response.data
        assert profile_data["cross_area_filter_available"] == filter_available

    @pytest.mark.parametrize(
        "permissions, area_limits, filter_available",
        [
            ([Permissions.GRIEVANCES_CROSS_AREA_FILTER], True, False),
            ([Permissions.GRIEVANCES_CROSS_AREA_FILTER], False, True),
            ([], True, False),
            ([], False, False),
        ],
    )
    def test_cross_area_filter_available_in_scope_program(
        self,
        permissions: list,
        area_limits: bool,
        filter_available: bool,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        if area_limits:
            area = AreaFactory()
            AdminAreaLimitedToFactory(partner=self.user.partner, program=self.program1, areas=[area])

        response = self.api_client.get(self.user_profile_url, {"program": self.program1.slug})
        assert response.status_code == status.HTTP_200_OK
        profile_data = response.data
        assert profile_data["cross_area_filter_available"] == filter_available


class TestUserList:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:accounts:users-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )
        self.count_url = reverse(
            "api:accounts:users-count",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, first_name="Alice")
        self.api_client = api_client(self.user)

        role = RoleFactory(name="TestRole", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value])
        self.user1 = UserFactory(partner=self.partner, first_name="Bob")
        RoleAssignmentFactory(user=self.user1, business_area=self.afghanistan, role=role)

        self.user2 = UserFactory(partner=self.partner, first_name="Carol")
        RoleAssignmentFactory(user=self.user2, business_area=self.afghanistan, program=self.program, role=role)

        partner_with_role_1 = PartnerFactory(name="TestPartner1")
        RoleAssignmentFactory(partner=partner_with_role_1, business_area=self.afghanistan, role=role)
        self.user3 = UserFactory(partner=partner_with_role_1, first_name="Dave")

        partner_with_role_2 = PartnerFactory(name="TestPartner2")
        RoleAssignmentFactory(
            partner=partner_with_role_2, business_area=self.afghanistan, program=self.program, role=role
        )
        self.user4 = UserFactory(partner=partner_with_role_2, first_name="Eve")

        self.user_in_different_ba = UserFactory(partner=self.partner, first_name="Frank")
        RoleAssignmentFactory(
            user=self.user_in_different_ba,
            business_area=create_ukraine(),
            role=role,
        )

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.USER_MANAGEMENT_VIEW_LIST], status.HTTP_200_OK),
            (ALL_GRIEVANCES_CREATE_MODIFY, status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
            ([Permissions.POPULATION_VIEW_HOUSEHOLDS_LIST], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_user_list_permissions(
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

        response = self.api_client.get(self.list_url)
        assert response.status_code == expected_status

    def test_user_list(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )

        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        response_results = response.json()["results"]
        assert len(response_results) == 5

        response_count = self.api_client.get(self.count_url)
        assert response_count.status_code == status.HTTP_200_OK
        assert response_count.json()["count"] == 5

        for i, user in enumerate([self.user, self.user1, self.user2, self.user3, self.user4]):
            user_result = response_results[i]
            assert user_result["id"] == str(user.id)
            assert user_result["first_name"] == user.first_name
            assert user_result["last_name"] == user.last_name
            assert user_result["email"] == user.email
            assert user_result["username"] == user.username

    @pytest.mark.parametrize(
        "permissions, expected_status",
        [
            ([Permissions.USER_MANAGEMENT_VIEW_LIST], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_user_count(
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
            assert response.json()["count"] == 5

    def test_user_list_caching(
        self, create_user_role_with_permissions: Any, set_admin_area_limits_in_program: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            program=self.program,
        )

        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag = response.headers["etag"]
            assert json.loads(cache.get(etag)[0].decode("utf8")) == response.json()
            assert len(response.json()["results"]) == 5
            assert len(ctx.captured_queries) == 9

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_second_call = response.headers["etag"]
            assert etag == etag_second_call
            assert len(ctx.captured_queries) == 4

        self.user2.first_name = "Zoe"
        self.user2.save()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_third_call = response.headers["etag"]
            assert json.loads(cache.get(etag_third_call)[0].decode("utf8")) == response.json()
            assert etag_third_call not in [etag, etag_second_call]
            # 4 queries are saved because of cached permissions calculations
            assert len(ctx.captured_queries) == 5

        self.user3.delete()
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fourth_call = response.headers["etag"]
            assert len(response.json()["results"]) == 4
            assert etag_fourth_call not in [etag, etag_second_call, etag_third_call, etag_third_call]
            assert len(ctx.captured_queries) == 5

        # no change - use cache
        with CaptureQueriesContext(connection) as ctx:
            response = self.api_client.get(self.list_url)
            assert response.status_code == status.HTTP_200_OK
            assert response.has_header("etag")
            etag_fifth_call = response.headers["etag"]
            assert etag_fifth_call == etag_fourth_call
            assert len(ctx.captured_queries) == 4


class TestProgramUsers:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.afghanistan.active = True
        self.afghanistan.save()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.list_url = reverse(
            "api:accounts:users-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, first_name="Alice")
        self.api_client = api_client(self.user)

        self.role1 = RoleFactory(
            name="TestRole1",
            permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value, Permissions.PROGRAMME_FINISH.value],
        )
        self.role2 = RoleFactory(name="TestRole2", permissions=[Permissions.POPULATION_VIEW_HOUSEHOLDS_DETAILS.value])
        self.role3 = RoleFactory(name="TestRole3", permissions=[Permissions.TARGETING_VIEW_LIST.value])
        self.role_p1 = RoleFactory(
            name="TestRoleP1", permissions=[Permissions.PM_CREATE.value, Permissions.PM_VIEW_LIST.value]
        )
        self.role_p2 = RoleFactory(name="TestRoleP2", permissions=[Permissions.ACCOUNTABILITY_SURVEY_VIEW_CREATE.value])

        self.user1 = UserFactory(
            partner=self.partner,
            first_name="Bob",
            last_login=timezone.make_aware(datetime.datetime.strptime("2021-01-11", "%Y-%m-%d")),
        )
        RoleAssignmentFactory(user=self.user1, business_area=self.afghanistan, role=self.role1)

        self.user2 = UserFactory(partner=self.partner, first_name="Carol")
        RoleAssignmentFactory(user=self.user2, business_area=self.afghanistan, program=self.program, role=self.role2)

        partner_with_role_1 = PartnerFactory(name="TestPartner1")
        RoleAssignmentFactory(partner=partner_with_role_1, business_area=self.afghanistan, role=self.role_p1)
        self.user3 = UserFactory(partner=partner_with_role_1, first_name="Dave")

        partner_with_role_2 = PartnerFactory(name="TestPartner2")
        RoleAssignmentFactory(
            partner=partner_with_role_2, business_area=self.afghanistan, program=self.program, role=self.role_p2
        )
        self.user4 = UserFactory(partner=partner_with_role_2, first_name="Eve")

        self.user5 = UserFactory(partner=partner_with_role_2, first_name="Frank")
        RoleAssignmentFactory(user=self.user5, business_area=self.afghanistan, program=self.program, role=self.role3)

        self.user_without_role = UserFactory(partner=self.partner, first_name="Gina")

        role_d1 = RoleFactory(name="TestRoleD1", permissions=[Permissions.GRIEVANCES_CREATE.value])
        role_d2 = RoleFactory(name="TestRoleD2", permissions=[Permissions.GRIEVANCES_UPDATE.value])
        self.user_in_different_program = UserFactory(partner=self.partner, first_name="Harry")
        program2 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        RoleAssignmentFactory(
            user=self.user_in_different_program,
            business_area=self.afghanistan,
            program=program2,
            role=role_d1,
        )

        self.user_in_different_ba = UserFactory(partner=self.partner, first_name="Ivy")
        RoleAssignmentFactory(
            user=self.user_in_different_ba,
            business_area=create_ukraine(),
            role=role_d2,
        )

    def test_program_users(
        self,
        create_user_role_with_permissions: Any,
    ) -> None:
        role_with_user_management_permissions = RoleFactory(
            name="Role For User",
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value],
        )
        RoleAssignmentFactory(
            user=self.user,
            business_area=self.afghanistan,
            program=None,
            role=role_with_user_management_permissions,
        )
        response = self.api_client.get(self.list_url, {"program": self.program.slug, "serializer": "program_users"})
        assert response.status_code == status.HTTP_200_OK

        response_results = response.data["results"]
        assert len(response_results) == 6

        for i, user in enumerate([self.user, self.user1, self.user2, self.user3, self.user4, self.user5]):
            user_result = response_results[i]
            assert user_result["id"] == str(user.id)
            assert user_result["username"] == user.username
            assert user_result["email"] == user.email
            assert user_result["first_name"] == user.first_name
            assert user_result["last_name"] == user.last_name
            assert user_result["is_superuser"] == user.is_superuser
            assert user_result["partner"] == {
                "id": user.partner.id,
                "name": user.partner.name,
            }
            assert user_result["cross_area_filter_available"] is False
            assert user_result["status"] == user.status
            assert user_result["last_login"] == (f"{user.last_login:%Y-%m-%dT%H:%M:%SZ}" if user.last_login else None)

        # self.user
        assert response_results[0]["partner_roles"] == []
        assert response_results[0]["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(role_with_user_management_permissions),
            }
        ]
        assert response_results[0]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in role_with_user_management_permissions.permissions},
            }
        ]
        assert response_results[0]["permissions_in_scope"] == {
            str(perm) for perm in role_with_user_management_permissions.permissions
        }

        # self.user1
        assert response_results[1]["partner_roles"] == []
        assert response_results[1]["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role1),
            },
        ]
        assert response_results[1]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in self.role1.permissions},
            }
        ]
        assert response_results[1]["permissions_in_scope"] == {str(perm) for perm in self.role1.permissions}

        # self.user2
        assert response_results[2]["partner_roles"] == []
        assert response_results[2]["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": self.program.name,
                "role": get_role_data(self.role2),
            },
        ]

        assert response_results[2]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in self.role2.permissions},
            }
        ]
        assert response_results[2]["permissions_in_scope"] == {str(perm) for perm in self.role2.permissions}

        # self.user3
        assert response_results[3]["partner_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": None,
                "role": get_role_data(self.role_p1),
            },
        ]
        assert response_results[3]["user_roles"] == []
        assert response_results[3]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in self.role_p1.permissions},
            }
        ]
        assert response_results[3]["permissions_in_scope"] == {str(perm) for perm in self.role_p1.permissions}

        # self.user4
        assert response_results[4]["partner_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": self.program.name,
                "role": get_role_data(self.role_p2),
            },
        ]
        assert response_results[4]["user_roles"] == []
        assert response_results[4]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in self.role_p2.permissions},
            }
        ]
        assert response_results[4]["permissions_in_scope"] == {str(perm) for perm in self.role_p2.permissions}

        # self.user5
        assert response_results[5]["partner_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": self.program.name,
                "role": get_role_data(self.role_p2),
            }
        ]
        assert response_results[5]["user_roles"] == [
            {
                "business_area": self.afghanistan.slug,
                "program": self.program.name,
                "role": get_role_data(self.role3),
            },
        ]
        assert response_results[5]["business_areas"] == [
            {
                **get_business_area_data(self.afghanistan),
                "permissions": {str(perm) for perm in [*self.role_p2.permissions, *self.role3.permissions]},
            }
        ]
        assert response_results[5]["permissions_in_scope"] == {
            str(perm) for perm in [*self.role_p2.permissions, *self.role3.permissions]
        }


class TestUserFilter:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program1 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.program2 = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:accounts:users-list",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
            },
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner, first_name="Alice")
        self.api_client = api_client(self.user)
        self.role_with_user_management_permissions = RoleFactory(
            name="Role For User",
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST.value],
        )
        RoleAssignmentFactory(
            user=self.user,
            business_area=self.afghanistan,
            program=None,
            role=self.role_with_user_management_permissions,
        )

        self.role1 = RoleFactory(name="TestRole1", permissions=[Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS.value])
        self.role2 = RoleFactory(name="TestRole2", permissions=[Permissions.PROGRAMME_REMOVE.value])

        self.user1 = UserFactory(partner=self.partner, first_name="Bob")
        RoleAssignmentFactory(user=self.user1, business_area=self.afghanistan, role=self.role1)

        self.user2 = UserFactory(partner=self.partner, first_name="Carol")
        RoleAssignmentFactory(user=self.user2, business_area=self.afghanistan, program=self.program1, role=self.role2)

        self.partner_with_role_1 = PartnerFactory(name="TestPartner1")
        RoleAssignmentFactory(partner=self.partner_with_role_1, business_area=self.afghanistan, role=self.role1)
        self.user3 = UserFactory(partner=self.partner_with_role_1, first_name="Dave")

        self.partner_with_role_2 = PartnerFactory(name="TestPartner2")
        RoleAssignmentFactory(
            partner=self.partner_with_role_2, business_area=self.afghanistan, program=self.program1, role=self.role2
        )
        self.user4 = UserFactory(partner=self.partner_with_role_2, first_name="Eve")

        self.user_in_different_program = UserFactory(partner=self.partner, first_name="Frank")
        RoleAssignmentFactory(
            user=self.user_in_different_program,
            business_area=self.afghanistan,
            program=self.program2,
            role=self.role1,
        )

        self.user_in_different_ba = UserFactory(partner=self.partner, first_name="George")
        RoleAssignmentFactory(
            user=self.user_in_different_ba,
            business_area=create_ukraine(),
            role=self.role2,
        )

    def test_filter_by_program(self) -> None:
        response = self.api_client.get(self.list_url, {"program": self.program1.slug})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 5
        users_ids = [result["id"] for result in response_results]
        assert str(self.user.id) in users_ids
        assert str(self.user1.id) in users_ids
        assert str(self.user2.id) in users_ids
        assert str(self.user3.id) in users_ids
        assert str(self.user4.id) in users_ids

        response_2 = self.api_client.get(self.list_url, {"program": self.program2.slug})
        assert response_2.status_code == status.HTTP_200_OK
        response_results_2 = response_2.data["results"]
        assert len(response_results_2) == 4
        users_ids_2 = [result["id"] for result in response_results_2]
        assert str(self.user.id) in users_ids_2
        assert str(self.user1.id) in users_ids_2
        assert str(self.user3.id) in users_ids_2
        assert str(self.user_in_different_program.id) in users_ids_2

    def test_filter_by_status(self) -> None:
        self.user2.status = INACTIVE
        self.user2.save()
        self.user_in_different_program.status = INACTIVE
        self.user_in_different_program.save()
        response = self.api_client.get(self.list_url, {"status": "INACTIVE"})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 2
        users_ids = [result["id"] for result in response_results]
        assert str(self.user2.id) in users_ids
        assert str(self.user_in_different_program.id) in users_ids

    def test_filter_by_partner(self) -> None:
        response = self.api_client.get(self.list_url, {"partner": self.partner_with_role_1.id})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user3.id)

    def test_filter_by_role(self) -> None:
        response = self.api_client.get(self.list_url, {"roles": str(self.role1.id)})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 3
        users_ids = [result["id"] for result in response_results]
        assert str(self.user1.id) in users_ids
        assert str(self.user3.id) in users_ids
        assert str(self.user_in_different_program.id) in users_ids

    def test_filter_by_is_ticket_creator(self) -> None:
        GrievanceTicketFactory(
            created_by=self.user2,
        )
        response = self.api_client.get(self.list_url, {"is_ticket_creator": True})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user2.id)

    def test_filter_by_is_survey_creator(self) -> None:
        SurveyFactory(
            created_by=self.user2,
        )
        response = self.api_client.get(self.list_url, {"is_survey_creator": False})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 5
        users_ids = [result["id"] for result in response_results]
        assert str(self.user.id) in users_ids
        assert str(self.user1.id) in users_ids
        assert str(self.user3.id) in users_ids
        assert str(self.user4.id) in users_ids
        assert str(self.user_in_different_program.id) in users_ids

    def test_filter_by_is_message_creator(self) -> None:
        Message.objects.create(
            created_by=self.user1,
            title="Test Message",
            business_area=self.afghanistan,
        )
        response = self.api_client.get(self.list_url, {"is_message_creator": True})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user1.id)

    def test_filter_by_is_feedback_creator(self) -> None:
        FeedbackFactory(
            created_by=self.user_in_different_program,
        )
        response = self.api_client.get(self.list_url, {"is_feedback_creator": True})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user_in_different_program.id)

    def test_search(self) -> None:
        response = self.api_client.get(self.list_url, {"search": "Bob"})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user1.id)

        self.user_in_different_program.email = "newemail@unicef.com"
        self.user_in_different_program.save()
        response = self.api_client.get(self.list_url, {"search": "new"})
        assert response.status_code == status.HTTP_200_OK
        response_results = response.data["results"]
        assert len(response_results) == 1
        assert response_results[0]["id"] == str(self.user_in_different_program.id)


class TestUserChoices:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.choices_url = "api:accounts:users-choices"
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        RoleFactory(name="TestRole")
        RoleFactory(name="TestRole2")
        RoleFactory(name="TestRole3")

        self.partner.allowed_business_areas.add(self.afghanistan)

        self.unicef_hq = PartnerFactory(name="UNICEF HQ")
        self.unicef_partner_in_afghanistan = PartnerFactory(name="UNICEF Partner for afghanistan")

    def test_get_choices(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
        )
        response = self.api_client.get(reverse(self.choices_url, kwargs={"business_area_slug": self.afghanistan.slug}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "role_choices": [
                dict(name=role.name, value=role.id, subsystem=role.subsystem) for role in Role.objects.order_by("name")
            ],
            "status_choices": to_choice_object(USER_STATUS_CHOICES),
            "partner_choices": [
                dict(name=partner.name, value=partner.id)
                for partner in [self.partner, self.unicef_hq, self.unicef_partner_in_afghanistan]
            ],
            # TODO: below assert can be removed after temporary solution is removed for partners
            "partner_choices_temp": [
                dict(name=partner.name, value=partner.id)
                for partner in [self.unicef_hq, self.unicef_partner_in_afghanistan]
            ],
        }


class TestPartnerForGrievanceChoices:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_partner_role_with_permissions: Any) -> None:
        self.partner_for_grievance_choices_url = "api:accounts:users-partner-for-grievance-choices"
        self.afghanistan = create_afghanistan()

        self.program = ProgramFactory(name="Test Program", status=Program.DRAFT, business_area=self.afghanistan)

        self.program_for_household = ProgramFactory(
            name="Test Program for Household", status=Program.DRAFT, business_area=self.afghanistan
        )
        self.household, individuals = create_household_and_individuals(
            household_data={
                "business_area": self.afghanistan,
                "program_id": self.program_for_household.pk,
            },
            individuals_data=[
                {
                    "business_area": self.afghanistan,
                    "program_id": self.program_for_household.pk,
                },
            ],
        )
        self.individual = individuals[0]

        # UNICEF partner
        partner_unicef, _ = Partner.objects.get_or_create(name="UNICEF")
        self.unicef_hq, _ = Partner.objects.get_or_create(name="UNICEF HQ", parent=partner_unicef)
        self.user = UserFactory(partner=self.unicef_hq, username="unicef_user")
        self.api_client = api_client(self.user)
        self.unicef_partner_for_afghanistan, _ = Partner.objects.get_or_create(
            name="UNICEF Partner for afghanistan", parent=partner_unicef
        )

        # partner with access to Test Program - should be returned if Program is passed or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        self.partner_with_access_to_test_program = PartnerFactory(name="Partner with access to Test Program")
        create_partner_role_with_permissions(
            self.partner_with_access_to_test_program, [], self.afghanistan, self.program
        )

        # partner with access to Test Program for Household - should be returned if Program is not passed and household/individual is passed
        # or if neither program nor household/individual is passed
        # (because it has access to ANY program in this BA)
        self.partner_with_access_to_test_program_for_hh = PartnerFactory(
            name="Partner with access to Test Program for Household"
        )
        create_partner_role_with_permissions(
            self.partner_with_access_to_test_program_for_hh, [], self.afghanistan, self.program_for_household
        )

        # partner with access to all programs - should be returned if neither program nor household/individual is passed
        # or if any program is passed or if household/individual is passed
        # (because it has access to all programs in this BA)
        self.partner_with_access_to_all_programs = PartnerFactory(name="Partner with access to All Programs")
        create_partner_role_with_permissions(
            self.partner_with_access_to_all_programs, [], self.afghanistan, whole_business_area_access=True
        )

        # partner without access to any program in this BA - should not be returned in any case
        self.unicef_without_program_access = PartnerFactory(name="Partner Without Program Access")

    def test_get_partner_for_grievance_choices_for_program(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(self.partner_for_grievance_choices_url, kwargs={"business_area_slug": self.afghanistan.slug}),
            {"program": self.program.slug},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                "name": self.partner_with_access_to_all_programs.name,
                "value": self.partner_with_access_to_all_programs.id,
            },
            {
                "name": self.partner_with_access_to_test_program.name,
                "value": self.partner_with_access_to_test_program.id,
            },
            {"name": self.unicef_hq.name, "value": self.unicef_hq.id},
            {"name": self.unicef_partner_for_afghanistan.name, "value": self.unicef_partner_for_afghanistan.id},
        ]

    def test_get_partner_for_grievance_choices_for_household(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(self.partner_for_grievance_choices_url, kwargs={"business_area_slug": self.afghanistan.slug}),
            {"household": self.household.pk},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                "name": self.partner_with_access_to_all_programs.name,
                "value": self.partner_with_access_to_all_programs.id,
            },
            {
                "name": self.partner_with_access_to_test_program_for_hh.name,
                "value": self.partner_with_access_to_test_program_for_hh.id,
            },
            {"name": self.unicef_hq.name, "value": self.unicef_hq.id},
            {"name": self.unicef_partner_for_afghanistan.name, "value": self.unicef_partner_for_afghanistan.id},
        ]

    def test_get_partner_for_grievance_choices_for_individual(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(self.partner_for_grievance_choices_url, kwargs={"business_area_slug": self.afghanistan.slug}),
            {"individual": self.individual.pk},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                "name": self.partner_with_access_to_all_programs.name,
                "value": self.partner_with_access_to_all_programs.id,
            },
            {
                "name": self.partner_with_access_to_test_program_for_hh.name,
                "value": self.partner_with_access_to_test_program_for_hh.id,
            },
            {"name": self.unicef_hq.name, "value": self.unicef_hq.id},
            {"name": self.unicef_partner_for_afghanistan.name, "value": self.unicef_partner_for_afghanistan.id},
        ]

    def test_get_partner_for_grievance_choices_without_params(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.USER_MANAGEMENT_VIEW_LIST],
            business_area=self.afghanistan,
            whole_business_area_access=True,
        )
        response = self.api_client.get(
            reverse(self.partner_for_grievance_choices_url, kwargs={"business_area_slug": self.afghanistan.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == [
            {
                "name": self.partner_with_access_to_all_programs.name,
                "value": self.partner_with_access_to_all_programs.id,
            },
            {
                "name": self.partner_with_access_to_test_program.name,
                "value": self.partner_with_access_to_test_program.id,
            },
            {
                "name": self.partner_with_access_to_test_program_for_hh.name,
                "value": self.partner_with_access_to_test_program_for_hh.id,
            },
            {"name": self.unicef_hq.name, "value": self.unicef_hq.id},
            {"name": self.unicef_partner_for_afghanistan.name, "value": self.unicef_partner_for_afghanistan.id},
        ]
