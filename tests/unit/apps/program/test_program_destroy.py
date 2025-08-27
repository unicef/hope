from typing import Any

from extras.test_utils.factories.account import PartnerFactory, UserFactory
from extras.test_utils.factories.core import create_afghanistan
from extras.test_utils.factories.program import ProgramFactory
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from hope.apps.account.permissions import Permissions
from hope.apps.program.models import Program

pytestmark = pytest.mark.django_db


class TestProgramDestroy:
    @pytest.fixture(autouse=True)
    def setup(self, api_client: Any, create_user_role_with_permissions: Any) -> None:
        self.afghanistan = create_afghanistan()
        self.program = ProgramFactory(business_area=self.afghanistan, status=Program.DRAFT)
        self.destroy_url = reverse(
            "api:programs:programs-detail",
            kwargs={
                "business_area_slug": self.afghanistan.slug,
                "slug": self.program.slug,
            },
        )
        self.partner = PartnerFactory(name="TestPartner")
        self.user = UserFactory(partner=self.partner)
        self.client = api_client(self.user)

    def test_program_destroy_without_permissions(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [], self.afghanistan, self.program)

        response = self.client.delete(self.destroy_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Program.objects.filter(id=self.program.id).exists()

    def test_program_destroy(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_REMOVE], self.afghanistan, self.program)

        response = self.client.delete(self.destroy_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Program.objects.filter(id=self.program.id).exists()

    def test_program_destroy_active(self, create_user_role_with_permissions: Any) -> None:
        create_user_role_with_permissions(self.user, [Permissions.PROGRAMME_REMOVE], self.afghanistan, self.program)
        self.program.status = Program.ACTIVE
        self.program.save()
        response = self.client.delete(self.destroy_url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == ["Only Draft Program can be deleted."]

        assert Program.objects.filter(id=self.program.id).exists()
