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


class TestPDUOnlineEditSendBack:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.pdu_edit_ready_authorized = PDUOnlineEditFactory(
            business_area=self.afghanistan,
            program=self.program,
            name="Ready Edit Authorized",
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
            name="Approved Edit",
            status=PDUOnlineEdit.Status.APPROVED,
            authorized_users=[self.user],
        )

    def _get_send_back_url(self, pdu_edit_id: int) -> str:
        return reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-send-back",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": pdu_edit_id,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_ONLINE_APPROVE], status.HTTP_200_OK),
            ([Permissions.PDU_TEMPLATE_CREATE], status.HTTP_403_FORBIDDEN),
            ([Permissions.PDU_ONLINE_SAVE_DATA], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_send_back_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        data = {"comment": "Please fix the data"}
        response = self.api_client.post(url, data=data)
        assert response.status_code == expected_status

    def test_send_back_success(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        comment_text = "Please review the vaccination data for accuracy"
        data = {"comment": comment_text}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "PDU Online Edit sent back successfully."}

        # Verify edit status changed
        self.pdu_edit_ready_authorized.refresh_from_db()
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

        # Verify comment was created
        assert PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_ready_authorized).exists()
        comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=self.pdu_edit_ready_authorized)
        assert comment.comment == comment_text
        assert comment.created_by == self.user
        assert comment.created_at is not None

    def test_send_back_not_authorized_user(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Attempt to send back an edit the user is not authorized for
        url = self._get_send_back_url(self.pdu_edit_ready_not_authorized.id)
        data = {"comment": "Please fix"}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_403_FORBIDDEN
        response_json = response.json()
        assert "You are not an authorized user for this PDU online edit." in response_json["detail"]

        # Verify no changes were made
        self.pdu_edit_ready_not_authorized.refresh_from_db()
        assert self.pdu_edit_ready_not_authorized.status == PDUOnlineEdit.Status.READY
        assert not PDUOnlineEditSentBackComment.objects.filter(
            pdu_online_edit=self.pdu_edit_ready_not_authorized
        ).exists()

    def test_send_back_invalid_status_new(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_new.id)
        data = {"comment": "Cannot send back NEW status"}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Ready' status and cannot be sent back." in response_json[0]

        # Verify no changes were made
        self.pdu_edit_new.refresh_from_db()
        assert self.pdu_edit_new.status == PDUOnlineEdit.Status.NEW
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_new).exists()

    def test_send_back_invalid_status_approved(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_approved.id)
        data = {"comment": "Cannot send back APPROVED status"}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "PDU Online Edit is not in the 'Ready' status and cannot be sent back." in response_json[0]

        # Verify no changes were made
        self.pdu_edit_approved.refresh_from_db()
        assert self.pdu_edit_approved.status == PDUOnlineEdit.Status.APPROVED
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_approved).exists()

    def test_send_back_empty_comment(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        data = {"comment": ""}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "comment" in response_json
        assert "This field may not be blank." in response_json["comment"]

        # Verify no changes were made
        self.pdu_edit_ready_authorized.refresh_from_db()
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_ready_authorized).exists()

    def test_send_back_missing_comment(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        data = {}  # No comment field
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "comment" in response_json
        assert "This field is required." in response_json["comment"]

        # Verify no changes were made
        self.pdu_edit_ready_authorized.refresh_from_db()
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_ready_authorized).exists()

    def test_send_back_null_comment(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        data = {"comment": None}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_json = response.json()
        assert "comment" in response_json
        assert "This field may not be null." in response_json["comment"]

        # Verify no changes were made
        self.pdu_edit_ready_authorized.refresh_from_db()
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.READY
        assert not PDUOnlineEditSentBackComment.objects.filter(pdu_online_edit=self.pdu_edit_ready_authorized).exists()

    def test_send_back_comment_with_leading_trailing_whitespace(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        comment_with_whitespace = "   Valid comment with whitespace   "
        expected_trimmed_comment = "Valid comment with whitespace"
        data = {"comment": comment_with_whitespace}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert response_json == {"message": "PDU Online Edit sent back successfully."}

        self.pdu_edit_ready_authorized.refresh_from_db()
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

        # Verify comment was created with trimmed content
        comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=self.pdu_edit_ready_authorized)
        assert comment.comment == expected_trimmed_comment
        assert comment.created_by == self.user

    def test_send_back_preserves_other_fields(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_ONLINE_APPROVE],
            business_area=self.afghanistan,
            program=self.program,
        )

        # Store original values
        original_name = self.pdu_edit_ready_authorized.name
        original_created_by = self.pdu_edit_ready_authorized.created_by
        original_created_at = self.pdu_edit_ready_authorized.created_at
        original_number_of_records = self.pdu_edit_ready_authorized.number_of_records
        original_authorized_users = list(self.pdu_edit_ready_authorized.authorized_users.all())

        url = self._get_send_back_url(self.pdu_edit_ready_authorized.id)
        data = {"comment": "Data needs revision"}
        response = self.api_client.post(url, data=data)

        assert response.status_code == status.HTTP_200_OK

        self.pdu_edit_ready_authorized.refresh_from_db()

        # Verify only status changed
        assert self.pdu_edit_ready_authorized.name == original_name
        assert self.pdu_edit_ready_authorized.created_by == original_created_by
        assert self.pdu_edit_ready_authorized.created_at == original_created_at
        assert self.pdu_edit_ready_authorized.number_of_records == original_number_of_records
        assert list(self.pdu_edit_ready_authorized.authorized_users.all()) == original_authorized_users

        # Verify status changed
        assert self.pdu_edit_ready_authorized.status == PDUOnlineEdit.Status.NEW

        # Verify comment was created
        comment = PDUOnlineEditSentBackComment.objects.get(pdu_online_edit=self.pdu_edit_ready_authorized)
        assert comment.comment == "Data needs revision"
        assert comment.created_by == self.user
