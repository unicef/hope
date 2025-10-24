from typing import Any, List

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.apps.periodic_data_update.models import PDUOnlineEdit, PDUOnlineEditSentBackComment
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditSendForApproval:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.pdu_edit_new_authorized = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="New Edit Authorized",
            status=PDUOnlineEdit.Status.NEW,
            authorized_users=[self.user],
        )

        self.pdu_edit_new_not_authorized = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="New Edit Not Authorized",
            status=PDUOnlineEdit.Status.NEW,
        )

        self.pdu_edit_ready = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit",
            status=PDUOnlineEdit.Status.READY,
            authorized_users=[self.user],
        )

        self.pdu_edit_approved = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Approved Edit",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
        )

    def _get_send_for_approval_url(self, pdu_edit_id: int) -> str:
        return reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-send-for-approval",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": pdu_edit_id,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_200_OK),
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_send_for_approval_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_for_approval_url(self.pdu_edit_new_authorized.id)
        response = self.api_client.post(url)
        assert response.status_code == expected_status

    def test_send_for_approval_success(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_for_approval_url(self.pdu_edit_new_authorized.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "PDU Online Edit sent for approval."}

        # Verify edit status changed from NEW to READY
        self.pdu_edit_new_authorized.refresh_from_db()
        assert self.pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY

    def test_send_for_approval_not_authorized_user(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_for_approval_url(self.pdu_edit_new_not_authorized.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert "You are not an authorized user for this PDU online edit." in response_json["detail"]

        # Verify no changes were made
        self.pdu_edit_new_not_authorized.refresh_from_db()
        assert self.pdu_edit_new_not_authorized.status == PDUOnlineEdit.Status.NEW

    def test_send_for_approval_invalid_status_ready(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_for_approval_url(self.pdu_edit_ready.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "Only new edits can be sent for approval." in response_json[0]

        # Verify no changes were made
        self.pdu_edit_ready.refresh_from_db()
        assert self.pdu_edit_ready.status == PDUOnlineEdit.Status.READY

    def test_send_for_approval_invalid_status_approved(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_for_approval_url(self.pdu_edit_approved.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "Only new edits can be sent for approval." in response_json[0]

        # Verify no changes were made
        self.pdu_edit_approved.refresh_from_db()
        assert self.pdu_edit_approved.status == PDUOnlineEdit.Status.APPROVED

    def test_send_for_approval_clears_sent_back_comment(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Create a sent back comment for the PDU edit
        comment = PDUOnlineEditSentBackComment.objects.create(
            comment="Please fix the data validation issues",
            created_by=self.user,
            pdu_online_edit=self.pdu_edit_new_authorized,
        )

        # Verify comment exists before sending for approval
        assert PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_new_authorized).exists()

        url = self._get_send_for_approval_url(self.pdu_edit_new_authorized.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "PDU Online Edit sent for approval."}

        # Verify edit status changed
        self.pdu_edit_new_authorized.refresh_from_db()
        assert self.pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY

        # Verify sent back comment was cleared
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_new_authorized).exists()
        assert not PDUOnlineEditSentBackComment.objects.filter(id=comment.id).exists()

    def test_send_for_approval_preserves_other_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_SAVE_DATA],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Store original values
        original_name = self.pdu_edit_new_authorized.name
        original_created_by = self.pdu_edit_new_authorized.created_by
        original_created_at = self.pdu_edit_new_authorized.created_at
        original_number_of_records = self.pdu_edit_new_authorized.number_of_records
        original_authorized_users = list(self.pdu_edit_new_authorized.authorized_users.all())

        url = self._get_send_for_approval_url(self.pdu_edit_new_authorized.id)
        response = self.api_client.post(url)

        assert response.status_code == status.HTTP_200_OK

        self.pdu_edit_new_authorized.refresh_from_db()

        # Verify other fields remain unchanged
        assert self.pdu_edit_new_authorized.name == original_name
        assert self.pdu_edit_new_authorized.created_by == original_created_by
        assert self.pdu_edit_new_authorized.created_at == original_created_at
        assert self.pdu_edit_new_authorized.number_of_records == original_number_of_records
        assert list(self.pdu_edit_new_authorized.authorized_users.all()) == original_authorized_users

        # Verify only status changed
        assert self.pdu_edit_new_authorized.status == PDUOnlineEdit.Status.READY

        # Verify approval fields are still empty
        assert self.pdu_edit_new_authorized.approved_by is None
        assert self.pdu_edit_new_authorized.approved_at is None
