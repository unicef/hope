from datetime import datetime
from typing import Any, List

from django.utils import timezone

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory, RoleFactory, RoleAssignmentFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory, PDUOnlineEditSentBackCommentFactory
from hope.apps.program.models import Program
from hope.apps.periodic_data_update.models import PDUOnlineEdit

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditDetail:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
    ) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)
        self.other_program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.api_client = api_client(self.user)

        self.partner_empty = PartnerFactory(name="EmptyPartner")
        self.user_can_save_data = UserFactory(partner=self.partner_empty, first_name="Alice")
        save_data_role = RoleFactory(name="Save Data", permissions=[Permissions.PDU_ONLINE_SAVE_DATA.value])
        RoleAssignmentFactory(
            user=self.user_can_save_data,
            role=save_data_role,
            business_area=self.afghanistan,
            program=self.program,
        )
        self.user_can_approve = UserFactory(partner=self.partner_empty, first_name="Bob")
        approve_role = RoleFactory(name="Approve", permissions=[Permissions.PDU_ONLINE_APPROVE.value])
        RoleAssignmentFactory(
            user=self.user_can_approve,
            role=approve_role,
            business_area=self.afghanistan,
            program=self.program,
        )
        self.user_can_all = UserFactory(partner=self.partner_empty, first_name="David")
        can_all_role = RoleFactory(
            name="Can All",
            permissions=[
                Permissions.PDU_ONLINE_SAVE_DATA.value,
                Permissions.PDU_ONLINE_APPROVE.value,
                Permissions.PDU_ONLINE_MERGE.value,
            ],
        )
        RoleAssignmentFactory(
            user=self.user_can_all,
            role=can_all_role,
            business_area=self.afghanistan,
            program=self.program,
        )
        partner_can_merge = PartnerFactory(name="Partner with PDU Permission")
        merge_role = RoleFactory(name="Merge", permissions=[Permissions.PDU_ONLINE_MERGE.value])
        self.user_partner_can_merge = UserFactory(partner=partner_can_merge, first_name="Eve")
        RoleAssignmentFactory(
            user=self.user_partner_can_merge,
            role=merge_role,
            business_area=self.afghanistan,
            program=self.program,
        )

        self.pdu_edit = PDUOnlineEditFactory(
            program=self.program,
            business_area=self.afghanistan,
            authorized_users=[self.user_partner_can_merge, self.user_can_all, self.user_can_approve],
            status=PDUOnlineEdit.Status.APPROVED,
            name="Test PDU Edit",
            number_of_records=100,
            created_by=self.user,
            approved_by=self.user_can_approve,
            approved_at=timezone.make_aware(datetime(year=2024, month=8, day=20)),
        )
        PDUOnlineEditSentBackCommentFactory(
            pdu_online_edit=self.pdu_edit,
            comment="This is a sent back comment.",
            created_by=self.user_can_approve,
        )

        self.url_detail = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "program_slug": self.program.slug,
                "pk": self.pdu_edit.pk,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
            ([Permissions.PROGRAMME_UPDATE], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pdu_online_edit_detail_permissions(
        self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_detail)
        assert response.status_code == expected_status

    def test_pdu_online_edit_detail(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.url_detail)
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["id"] == self.pdu_edit.id
        assert result["name"] == self.pdu_edit.name
        assert result["number_of_records"] == self.pdu_edit.number_of_records
        assert result["created_by"] == self.pdu_edit.created_by.get_full_name()
        assert result["created_at"] == f"{self.pdu_edit.created_at:%Y-%m-%dT%H:%M:%S.%fZ}"
        assert result["status"] == self.pdu_edit.status
        assert result["status_display"] == self.pdu_edit.get_status_display()
        assert result["is_authorized"] is False
        assert result["is_creator"] is True
        assert result["approved_by"] == self.pdu_edit.approved_by.get_full_name()
        assert result["approved_at"] == f"{self.pdu_edit.approved_at:%Y-%m-%dT%H:%M:%SZ}"
        assert result["sent_back_comment"] == {
            "comment": self.pdu_edit.sent_back_comment.comment,
            "created_by": self.pdu_edit.sent_back_comment.created_by.get_full_name(),
            "created_at": f"{self.pdu_edit.sent_back_comment.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
        }
        assert result["edit_data"] == self.pdu_edit.edit_data
        assert result["authorized_users"] == [
            {
                "id": str(self.user_can_approve.id),
                "first_name": self.user_can_approve.first_name,
                "last_name": self.user_can_approve.last_name,
                "username": self.user_can_approve.username,
                "email": self.user_can_approve.email,
                "pdu_permissions": [Permissions.PDU_ONLINE_APPROVE.value],
            },
            {
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
            },
            {
                "id": str(self.user_partner_can_merge.id),
                "first_name": self.user_partner_can_merge.first_name,
                "last_name": self.user_partner_can_merge.last_name,
                "username": self.user_partner_can_merge.username,
                "email": self.user_partner_can_merge.email,
                "pdu_permissions": [Permissions.PDU_ONLINE_MERGE.value],
            },
        ]
