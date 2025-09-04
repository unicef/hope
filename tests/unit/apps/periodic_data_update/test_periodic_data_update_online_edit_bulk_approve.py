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


class TestPDUOnlineEditBulkApprove:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.pdu_edit_ready_1 = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit 1",
            status=PDUOnlineEdit.Status.READY,
            authorized_users=[self.user],
        )

        self.pdu_edit_ready_2 = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit 2",
            status=PDUOnlineEdit.Status.READY,
            authorized_users=[self.user],
        )
        self.pdu_edit_ready_not_authorized = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit Not Authorized",
            status=PDUOnlineEdit.Status.READY,
        )

        self.pdu_edit_new = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="New Edit",
            status=PDUOnlineEdit.Status.NEW,
            authorized_users=[self.user],
        )

        self.pdu_edit_approved = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Already Approved Edit",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
        )

        self.url_bulk_approve = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-bulk-approve",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_200_OK),
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_bulk_approve_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_ready_1.id, self.pdu_edit_ready_2.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)
        assert response.status_code == expected_status

    def test_bulk_approve_check_authorized_user_single_edit(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Attempt to approve an edit the user is not authorized for
        data = {"ids": [self.pdu_edit_ready_not_authorized.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert (
            f"You are not an authorized user for PDU Online Edit: {self.pdu_edit_ready_not_authorized.id}"
            in response_json["detail"]
        )

        # Verify the edit was not approved
        self.pdu_edit_ready_not_authorized.refresh_from_db()
        assert self.pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY

    def test_bulk_approve_check_authorized_user_mixed(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Attempt to approve an edit the user is not authorized for
        data = {"ids": [self.pdu_edit_ready_not_authorized.id, self.pdu_edit_ready_1.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert (
            f"You are not an authorized user for PDU Online Edit: {self.pdu_edit_ready_not_authorized.id}"
            in response_json["detail"]
        )

        # Verify no edits were approved
        self.pdu_edit_ready_not_authorized.refresh_from_db()
        self.pdu_edit_ready_1.refresh_from_db()
        assert self.pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY
        assert self.pdu_edit_ready_1.status == PDUOnlineEdit.Status.READY

    def test_bulk_approve_success(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_ready_1.id, self.pdu_edit_ready_2.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "2 PDU Online Edits approved successfully."}

        # Verify edits were approved
        self.pdu_edit_ready_1.refresh_from_db()
        self.pdu_edit_ready_2.refresh_from_db()

        assert self.pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED
        assert self.pdu_edit_ready_1.approved_by == self.user
        assert self.pdu_edit_ready_1.approved_at is not None

        assert self.pdu_edit_ready_2.status == PDUOnlineEdit.Status.APPROVED
        assert self.pdu_edit_ready_2.approved_by == self.user
        assert self.pdu_edit_ready_2.approved_at is not None

    def test_bulk_approve_single_edit(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": [self.pdu_edit_ready_1.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "1 PDU Online Edits approved successfully."}

        self.pdu_edit_ready_1.refresh_from_db()
        assert self.pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED

    def test_bulk_approve_invalid_status(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Try to approve edits that are not in READY status
        data = {"ids": [self.pdu_edit_ready_1.id, self.pdu_edit_new.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Ready' status and cannot be approved." in response_json[0]

        # Verify no edits were approved
        self.pdu_edit_ready_1.refresh_from_db()
        self.pdu_edit_new.refresh_from_db()
        assert self.pdu_edit_ready_1.status == PDUOnlineEdit.Status.READY
        assert self.pdu_edit_new.status == PDUOnlineEdit.Status.NEW

    def test_bulk_approve_mixed_statuses(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Try to approve mix of READY, NEW, and APPROVED edits
        data = {"ids": [self.pdu_edit_ready_1.id, self.pdu_edit_new.id, self.pdu_edit_approved.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Ready' status and cannot be approved." in response_json[0]

    def test_bulk_approve_empty_ids(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        data = {"ids": []}
        response = self.api_client.post(self.url_bulk_approve, data=data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "This list may not be empty." in response_json["ids"][0]

    def test_bulk_approve_non_existent_ids(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        non_existent_id = 99999
        data = {"ids": [non_existent_id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "One or more PDU online edits not found." in response_json[0]

    def test_bulk_approve_preserves_other_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Store original values
        original_name = self.pdu_edit_ready_1.name
        original_created_by = self.pdu_edit_ready_1.created_by
        original_created_at = self.pdu_edit_ready_1.created_at
        original_number_of_records = self.pdu_edit_ready_1.number_of_records

        data = {"ids": [self.pdu_edit_ready_1.id]}
        response = self.api_client.post(self.url_bulk_approve, data=data)

        assert response.status_code == status.HTTP_200_OK

        self.pdu_edit_ready_1.refresh_from_db()

        # Verify only approval-related fields changed
        assert self.pdu_edit_ready_1.name == original_name
        assert self.pdu_edit_ready_1.created_by == original_created_by
        assert self.pdu_edit_ready_1.created_at == original_created_at
        assert self.pdu_edit_ready_1.number_of_records == original_number_of_records

        # Verify approval fields were updated
        assert self.pdu_edit_ready_1.status == PDUOnlineEdit.Status.APPROVED
        assert self.pdu_edit_ready_1.approved_by == self.user
        assert self.pdu_edit_ready_1.approved_at is not None
