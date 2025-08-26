from typing import Any, List

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory, RoleAssignmentFactory, RoleFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.api.serializers import PDU_ONLINE_EDIT_RELATED_PERMISSIONS
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditUsersAvailable:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.partner_empty = PartnerFactory(name="EmptyPartner")

        # Test Users; will be ordered alphabetically by first name

        # User with save data permission
        self.user_can_save_data = UserFactory(
            partner=self.partner_empty, first_name="Alice", last_name="Johnson", email="alice.johnson@test.com"
        )
        save_data_role = RoleFactory(name="Save Data", permissions=[Permissions.PDU_ONLINE_SAVE_DATA.value])
        RoleAssignmentFactory(
            user=self.user_can_save_data,
            role=save_data_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        # User with approve permission
        self.user_can_approve = UserFactory(
            partner=self.partner_empty, first_name="Bob", last_name="Smith", email="bob.smith@example.org"
        )
        approve_role = RoleFactory(name="Approve", permissions=[Permissions.PDU_ONLINE_APPROVE.value])
        RoleAssignmentFactory(
            user=self.user_can_approve,
            role=approve_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        # User with merge permission
        self.user_can_merge = UserFactory(
            partner=self.partner_empty, first_name="Charlie", last_name="Brown", email="charlie.brown@company.com"
        )
        merge_role = RoleFactory(name="Merge", permissions=[Permissions.PDU_ONLINE_MERGE.value])
        RoleAssignmentFactory(
            user=self.user_can_merge,
            role=merge_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        # User with all PDU permissions
        self.user_can_all = UserFactory(
            partner=self.partner_empty, first_name="David", last_name="Wilson", email="d.wilson@hope.org"
        )
        can_all_role = RoleFactory(
            permissions=[
                Permissions.PDU_ONLINE_SAVE_DATA.value,
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
            ]
        )
        RoleAssignmentFactory(
            user=self.user_can_all,
            role=can_all_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        # User with PDU permissions on Partner
        partner_can_all = PartnerFactory(name="Partner with PDU Permissions")
        self.user_partner_can_all = UserFactory(
            partner=partner_can_all, first_name="Eve", last_name="Davis", email="eve.davis@partner.org"
        )
        RoleAssignmentFactory(
            user=self.user_partner_can_all,
            role=can_all_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        self.user_can_approve_in_whole_ba = UserFactory(
            partner=self.partner_empty, first_name="Grace", last_name="Chen", email="grace.chen@global.org"
        )
        RoleAssignmentFactory(
            user=self.user_can_approve_in_whole_ba,
            role=approve_role,
            business_area=self.afghanistan,
            program=None,  # Permission in whole business area
        )

        # User with no PDU permissions
        self.user_without_permissions = UserFactory(
            partner=self.partner_empty, first_name="Frank", last_name="Miller", email="frank.miller@test.com"
        )
        no_pdu_role = RoleFactory(name="No Permissions", permissions=[Permissions.PROGRAMME_UPDATE.value])
        RoleAssignmentFactory(
            user=self.user_without_permissions,
            role=no_pdu_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        self.url_users_available = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-users-available",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.PDU_TEMPLATE_CREATE],
                status.HTTP_200_OK,
            ),
            (
                [Permissions.PROGRAMME_UPDATE],
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_users_available_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available)
        assert response.status_code == expected_status

    def test_users_available_list(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 6
        user_ids = {user["id"] for user in results}
        assert str(self.user_can_save_data.id) in user_ids
        assert str(self.user_can_approve.id) in user_ids
        assert str(self.user_can_merge.id) in user_ids
        assert str(self.user_can_all.id) in user_ids
        assert str(self.user_partner_can_all.id) in user_ids
        assert str(self.user_can_approve_in_whole_ba.id) in user_ids
        assert str(self.user_without_permissions.id) not in user_ids

        assert results[0] == {
            "id": str(self.user_can_save_data.id),
            "first_name": self.user_can_save_data.first_name,
            "last_name": self.user_can_save_data.last_name,
            "username": self.user_can_save_data.username,
            "email": self.user_can_save_data.email,
            "pdu_permissions": [Permissions.PDU_ONLINE_SAVE_DATA.value],
        }
        assert results[1] == {
            "id": str(self.user_can_approve.id),
            "first_name": self.user_can_approve.first_name,
            "last_name": self.user_can_approve.last_name,
            "username": self.user_can_approve.username,
            "email": self.user_can_approve.email,
            "pdu_permissions": [Permissions.PDU_ONLINE_APPROVE.value],
        }
        assert results[2] == {
            "id": str(self.user_can_merge.id),
            "first_name": self.user_can_merge.first_name,
            "last_name": self.user_can_merge.last_name,
            "username": self.user_can_merge.username,
            "email": self.user_can_merge.email,
            "pdu_permissions": [Permissions.PDU_ONLINE_MERGE.value],
        }
        assert results[3] == {
            "id": str(self.user_can_all.id),
            "first_name": self.user_can_all.first_name,
            "last_name": self.user_can_all.last_name,
            "username": self.user_can_all.username,
            "email": self.user_can_all.email,
            "pdu_permissions": [
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
                Permissions.PDU_ONLINE_SAVE_DATA.value,
            ],
        }
        assert results[4] == {
            "id": str(self.user_partner_can_all.id),
            "first_name": self.user_partner_can_all.first_name,
            "last_name": self.user_partner_can_all.last_name,
            "username": self.user_partner_can_all.username,
            "email": self.user_partner_can_all.email,
            "pdu_permissions": [
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
                Permissions.PDU_ONLINE_SAVE_DATA.value,
            ],
        }
        assert results[5] == {
            "id": str(self.user_can_approve_in_whole_ba.id),
            "first_name": self.user_can_approve_in_whole_ba.first_name,
            "last_name": self.user_can_approve_in_whole_ba.last_name,
            "username": self.user_can_approve_in_whole_ba.username,
            "email": self.user_can_approve_in_whole_ba.email,
            "pdu_permissions": [
                Permissions.PDU_ONLINE_APPROVE.value,
            ],
        }

    @pytest.mark.parametrize("permission", [p.value for p in PDU_ONLINE_EDIT_RELATED_PERMISSIONS])
    def test_users_available_filter_by_permission(
        self, permission: str, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"permission": permission})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        if permission == Permissions.PDU_ONLINE_SAVE_DATA.value:
            assert len(results) == 3
            user_ids = {user["id"] for user in results}
            assert str(self.user_can_save_data.id) in user_ids
            assert str(self.user_can_all.id) in user_ids
            assert str(self.user_partner_can_all.id) in user_ids
        elif permission == Permissions.PDU_ONLINE_APPROVE.value:
            assert len(results) == 4
            user_ids = {user["id"] for user in results}
            assert str(self.user_can_approve.id) in user_ids
            assert str(self.user_can_all.id) in user_ids
            assert str(self.user_partner_can_all.id) in user_ids
            assert str(self.user_can_approve_in_whole_ba.id) in user_ids
        elif permission == Permissions.PDU_ONLINE_MERGE.value:
            assert len(results) == 3
            user_ids = {user["id"] for user in results}
            assert str(self.user_can_merge.id) in user_ids
            assert str(self.user_can_all.id) in user_ids
            assert str(self.user_partner_can_all.id) in user_ids

    def test_users_available_filter_by_invalid_permission(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"permission": Permissions.PROGRAMME_UPDATE.value})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid permission" in response.json()[0]

    # Search functionality tests using existing users

    def test_users_available_search_by_first_name(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "Alice"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_save_data.id)
        assert results[0]["first_name"] == "Alice"

    def test_users_available_search_by_last_name(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "Brown"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_merge.id)
        assert results[0]["last_name"] == "Brown"

    def test_users_available_search_by_email(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "bob.smith@example.org"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_approve.id)
        assert results[0]["email"] == "bob.smith@example.org"

    def test_users_available_search_by_full_name(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "David Wilson"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_all.id)
        assert results[0]["first_name"] == "David"
        assert results[0]["last_name"] == "Wilson"

    def test_users_available_search_by_full_name_reversed(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "Davis Eve"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_partner_can_all.id)
        assert results[0]["first_name"] == "Eve"
        assert results[0]["last_name"] == "Davis"

    def test_users_available_search_partial_match(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "Char"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_merge.id)
        assert results[0]["first_name"] == "Charlie"

    def test_users_available_search_case_insensitive(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "ALICE JOHNSON"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_save_data.id)

    def test_users_available_search_no_results(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": "NonExistentUser"})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        assert len(results) == 0

    def test_users_available_search_empty_string(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_users_available, {"search": ""})
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        # Should return all users (same as no search)
        assert len(results) == 6

    def test_users_available_search_with_permission_filter(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(
            self.url_users_available, {"search": "David", "permission": Permissions.PDU_ONLINE_SAVE_DATA.value}
        )
        assert response.status_code == status.HTTP_200_OK
        results = response.json()

        # Should return David who has save data permission
        assert len(results) == 1
        assert results[0]["id"] == str(self.user_can_all.id)
        assert results[0]["first_name"] == "David"
