from typing import Any, Callable

import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
from hope.apps.account.permissions import Permissions
from hope.models.program import Program

pytestmark = pytest.mark.django_db


class TestProgramActivate:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.partner = PartnerFactory(name="Test Partner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

        self.program = ProgramFactory(
            business_area=self.afghanistan,
            status=Program.DRAFT,
            name="Test Program For Activate",
        )

        self.activate_url = reverse(
            "api:programs:programs-activate",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program.slug,
            },
        )

    @pytest.mark.parametrize(
        ("permissions", "expected_status"),
        [
            ([Permissions.PROGRAMME_ACTIVATE], status.HTTP_200_OK),
            ([Permissions.PROGRAMME_VIEW_LIST_AND_DETAILS], status.HTTP_403_FORBIDDEN),
            ([], status.HTTP_403_FORBIDDEN),
        ],
    )
    def test_activate_program_permissions(
        self,
        permissions: list,
        expected_status: int,
        create_user_role_with_permissions: Callable,
    ) -> None:
        create_user_role_with_permissions(self.user, permissions, self.afghanistan, whole_business_area_access=True)
        assert self.program.status == Program.DRAFT

        response = self.client.post(self.activate_url)
        assert response.status_code == expected_status
        self.program.refresh_from_db()

        if expected_status == status.HTTP_200_OK:
            assert self.program.status == Program.ACTIVE
            assert response.json() == {"message": "Program Activated."}
        else:
            assert self.program.status == Program.DRAFT  # Status should not change if permission denied

    def test_activate_program_already_active(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_ACTIVATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        self.program.status = Program.ACTIVE
        self.program.save()

        response = self.client.post(self.activate_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Program is already active." in response.json()

        self.program.refresh_from_db()
        assert self.program.status == Program.ACTIVE

    def test_activate_program_status_finished(self, create_user_role_with_permissions: Callable) -> None:
        create_user_role_with_permissions(
            self.user,
            [Permissions.PROGRAMME_ACTIVATE],
            self.afghanistan,
            whole_business_area_access=True,
        )
        self.program.status = Program.FINISHED
        self.program.save()

        response = self.client.post(self.activate_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Program Activated."}

        self.program.refresh_from_db()
        assert self.program.status == Program.ACTIVE
