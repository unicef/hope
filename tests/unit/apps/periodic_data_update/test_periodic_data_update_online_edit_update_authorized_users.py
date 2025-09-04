from typing import Any, List

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.models import PDUOnlineEdit
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditUpdateAuthorizedUsers:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.creator = UserFactory(partner=self.partner)
        self.other_user = UserFactory(partner=self.partner)
        self.authorized_user1 = UserFactory(partner=self.partner)
        self.authorized_user2 = UserFactory(partner=self.partner)
        self.authorized_user3 = UserFactory(partner=self.partner)

        self.api_client = api_client(self.creator)

        # Create test PDU online edits in different statuses
        self.pdu_edit_new = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="New Edit",
            status=PDUOnlineEdit.Status.NEW,
            created_by=self.creator,
            authorized_users=[self.authorized_user1],
        )

        self.pdu_edit_ready = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit",
            status=PDUOnlineEdit.Status.READY,
            created_by=self.creator,
            authorized_users=[self.authorized_user1, self.authorized_user2],
        )

        self.pdu_edit_approved = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Approved Edit",
            status=PDUOnlineEdit.Status.APPROVED,
            created_by=self.creator,
            authorized_users=[self.authorized_user1],
        )

        # PDU edit created by different user
        self.pdu_edit_other_creator = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Other Creator Edit",
            status=PDUOnlineEdit.Status.NEW,
            created_by=self.other_user,
            authorized_users=[self.authorized_user1],
        )

    def _get_update_authorized_users_url(self, pdu_edit_id: int) -> str:
        return reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-update-authorized-users",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": pdu_edit_id,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_200_OK),
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_update_authorized_users_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {"authorized_users": [self.authorized_user1.id, self.authorized_user2.id]}
        response = self.api_client.post(url, data=data)
        assert response.status_code == expected_status

    def test_update_authorized_users_success_add_users(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state - only authorized_user1
        initial_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(initial_authorized_users) == 1
        assert self.authorized_user1 in initial_authorized_users

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {"authorized_users": [self.authorized_user1.id, self.authorized_user2.id, self.authorized_user3.id]}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "Authorized users updated successfully."}

        # Verify users were added
        self.pdu_edit_new.refresh_from_db()
        updated_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(updated_authorized_users) == 3
        assert self.authorized_user1 in updated_authorized_users
        assert self.authorized_user2 in updated_authorized_users
        assert self.authorized_user3 in updated_authorized_users

    def test_update_authorized_users_success_remove_users(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state - has authorized_user1 and authorized_user2
        initial_authorized_users = list(self.pdu_edit_ready.authorized_users.all())
        assert len(initial_authorized_users) == 2
        assert self.authorized_user1 in initial_authorized_users
        assert self.authorized_user2 in initial_authorized_users

        url = self._get_update_authorized_users_url(self.pdu_edit_ready.id)
        data = {"authorized_users": [self.authorized_user1.id]}  # Remove authorized_user2
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "Authorized users updated successfully."}

        # Verify user was removed
        self.pdu_edit_ready.refresh_from_db()
        updated_authorized_users = list(self.pdu_edit_ready.authorized_users.all())
        assert len(updated_authorized_users) == 1
        assert self.authorized_user1 in updated_authorized_users
        assert self.authorized_user2 not in updated_authorized_users

    def test_update_authorized_users_success_replace_all_users(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state
        initial_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(initial_authorized_users) == 1
        assert self.authorized_user1 in initial_authorized_users

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {
            "authorized_users": [self.authorized_user2.id, self.authorized_user3.id]
        }  # Replace with different users
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK

        # Verify users were completely replaced
        self.pdu_edit_new.refresh_from_db()
        updated_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(updated_authorized_users) == 2
        assert self.authorized_user1 not in updated_authorized_users
        assert self.authorized_user2 in updated_authorized_users
        assert self.authorized_user3 in updated_authorized_users

    def test_update_authorized_users_success_clear_all_users(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Verify initial state
        initial_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(initial_authorized_users) == 1

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {"authorized_users": []}  # Clear all users
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK

        # Verify all users were removed
        self.pdu_edit_new.refresh_from_db()
        updated_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(updated_authorized_users) == 0

    def test_update_authorized_users_not_creator(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_update_authorized_users_url(self.pdu_edit_other_creator.id)
        data = {"authorized_users": [self.authorized_user2.id]}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "Only the creator of the PDU Online Edit can update authorized users." in response_json[0]

        # Verify no changes were made
        self.pdu_edit_new.refresh_from_db()
        original_authorized_users = list(self.pdu_edit_other_creator.authorized_users.all())
        assert len(original_authorized_users) == 1
        assert self.authorized_user1 in original_authorized_users

    def test_update_authorized_users_works_in_all_statuses(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        test_cases = [
            (self.pdu_edit_new, PDUOnlineEdit.Status.NEW),
            (self.pdu_edit_ready, PDUOnlineEdit.Status.READY),
            (self.pdu_edit_approved, PDUOnlineEdit.Status.APPROVED),
        ]

        for pdu_edit, expected_status in test_cases:
            url = self._get_update_authorized_users_url(pdu_edit.id)
            data = {"authorized_users": [self.authorized_user3.id]}
            response = self.api_client.post(url, data=data)

            assert response.status_code == status.HTTP_200_OK, f"Failed for status {expected_status}"

            # Verify changes were made
            pdu_edit.refresh_from_db()
            updated_authorized_users = list(pdu_edit.authorized_users.all())
            assert len(updated_authorized_users) == 1
            assert self.authorized_user3 in updated_authorized_users

            # Verify status remained unchanged
            assert pdu_edit.status == expected_status

    def test_update_authorized_users_invalid_user_id(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {"authorized_users": [self.authorized_user3.id, 99999]}  # Mix of valid and invalid
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "authorized_users" in response_json

        # Verify no changes were made
        self.pdu_edit_new.refresh_from_db()
        original_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(original_authorized_users) == 1
        assert self.authorized_user1 in original_authorized_users

    def test_update_authorized_users_missing_field(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.creator,
            permissions=[Permissions.PDU_TEMPLATE_CREATE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_update_authorized_users_url(self.pdu_edit_new.id)
        data = {}  # Missing authorized_users field
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "authorized_users" in response_json
        assert "This field is required." in response_json["authorized_users"]

        # Verify no changes were made
        self.pdu_edit_new.refresh_from_db()
        original_authorized_users = list(self.pdu_edit_new.authorized_users.all())
        assert len(original_authorized_users) == 1
        assert self.authorized_user1 in original_authorized_users
