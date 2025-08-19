from typing import Any, List

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory, RoleFactory, RoleAssignmentFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from extras.test_utils.factories.periodic_data_update import PDUOnlineEditFactory
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db(transaction=True)


class TestPDUOnlineEditList:
    @pytest.fixture(autouse=True)
    def setup(
        self,
        api_client: Any,
    ) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.other_program = ProgramFactory(business_area=self.afghanistan, status=Program.ACTIVE)

        self.list_url = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-list",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )
        self.count_url = reverse(
            "api:periodic-data-update:periodic-data-update-online-edits-count",
            kwargs={"business_area_slug": self.afghanistan.slug, "program_slug": self.program.slug},
        )

        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        RoleAssignmentFactory(
            user=self.user,
            role=RoleFactory(name="Save Data", permissions=[Permissions.PDU_ONLINE_SAVE_DATA.value]),
            business_area=self.afghanistan,
            program=self.program,
        )
        self.api_client = api_client(self.user)

        user_other = UserFactory(partner=self.partner, first_name="Charlie")

        self.pdu_edit1 = PDUOnlineEditFactory(program=self.program, business_area=self.afghanistan, authorized_users=[user_other])
        self.pdu_edit2 = PDUOnlineEditFactory(program=self.program, business_area=self.afghanistan, authorized_users=[self.user])  # Request user is authorized
        self.pdu_edit_other_program = PDUOnlineEditFactory(program=self.other_program, business_area=self.afghanistan)

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            (
                [Permissions.PDU_VIEW_LIST_AND_DETAILS],
                status.HTTP_200_OK,
            ),
            (
                [Permissions.PROGRAMME_UPDATE],
                status.HTTP_403_FORBIDDEN,
            ),
        ],
    )
    def test_pdu_online_edit_list_permissions(
            self, permissions: List, expected_status: int, create_user_role_with_permissions: Any
    ) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.list_url)
        assert response.status_code == expected_status

    def test_pdu_online_edit_list(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=[Permissions.PDU_VIEW_LIST_AND_DETAILS],
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        results = response.json()["results"]
        assert len(results) == 2
        result_ids = {item["id"] for item in results}
        assert self.pdu_edit1.id in result_ids
        assert self.pdu_edit2.id in result_ids
        assert self.pdu_edit_other_program.id not in result_ids

        assert results == [
            {
                "id": self.pdu_edit1.id,
                "name": self.pdu_edit1.name,
                "number_of_records": self.pdu_edit1.number_of_records,
                "created_by": self.pdu_edit1.created_by.get_full_name(),
                "created_at": f"{self.pdu_edit1.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
                "status": self.pdu_edit1.combined_status,
                "status_display": self.pdu_edit1.combined_status_display,
                "is_authorized": False,
            },
            {
                "id": self.pdu_edit2.id,
                "name": self.pdu_edit2.name,
                "number_of_records": self.pdu_edit2.number_of_records,
                "created_by": self.pdu_edit2.created_by.get_full_name(),
                "created_at": f"{self.pdu_edit2.created_at:%Y-%m-%dT%H:%M:%S.%fZ}",
                "status": self.pdu_edit2.combined_status,
                "status_display": self.pdu_edit2.combined_status_display,
                "is_authorized": True,
            },
        ]

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PDU_VIEW_LIST_AND_DETAILS], status.HTTP_200_OK),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_pdu_online_edit_count(self, permissions: list, expected_status: int, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(
            user=self.user,
            permissions=permissions,
            business_area=self.afghanistan,
            program=self.program,
        )
        response = self.api_client.get(self.count_url)
        assert response.status_code == expected_status
        if expected_status == status.HTTP_200_OK:
            assert response.json()["count"] == 2
